#include "cwCommon.h"
#include "cwLog.h"
#include "cwCommonImpl.h"
#include "cwMem.h"
#include "cwFileSys.h"
#include "cwTextBuf.h"
#include "cwLex.h"
#include "cwText.h"
#include "cwNumericConvert.h"
#include "cwObject.h"
#include "cwVectOps.h"
#include "cwMtx.h"
#include "cwThread.h"
#include "cwSpScBuf.h"
#include "cwSpScQueueTmpl.h"
#include "cwThreadMach.h"
#include "cwSerialPort.h"
#include "cwSerialPortSrv.h"
#include "cwSocket.h"
#include "cwUtility.h"
#include "cwDsp.h"

#if defined(cwWEBSOCK)
#include "cwWebSock.h"
#include "cwWebSockSvr.h"
#include "cwUi.h"
#include "cwUiTest.h"
#endif

#include "cwTime.h"
#include "cwMidi.h"
#include "cwAudioDevice.h"

#if defined(cwALSA)
#include "cwMidiPort.h"
#include "cwAudioDeviceTest.h"
#include "cwAudioDeviceAlsa.h"
#endif

#include "cwAudioBuf.h"
#include "cwTcpSocket.h"
#include "cwTcpSocketSrv.h"
#include "cwTcpSocketTest.h"


#include "cwMdns.h"
#include "cwDnsSd.h"
#include "cwEuCon.h"
#if defined(cwWEBSOCK)
#include "cwIo.h"
#include "cwIoTest.h"
#endif

#include "cwDataSets.h"
#include "cwSvg.h"
#include "cwAudioFile.h"
#include "cwAudioFileOps.h"

//#include "cwNbMem.h"

#include <iostream>


unsigned calc( unsigned n )
{ return n; }

template<typename T0, typename T1, typename... ARGS>
  unsigned calc( T0 n, T1 i, ARGS&&... args)
{  
  return calc(n + i, std::forward<ARGS>(args)...);
}

void print()
{
  printf("\n");
}

template<typename T0, typename T1, typename ...ARGS>
  void print(T0 t0, T1 t1, ARGS&&... args)
{
  static const unsigned short int size = sizeof...(ARGS);
  std::cout << t0 << ":" << t1 << " (" << size << "), ";
  print(std::forward<ARGS>(args)...);
}

void get(int)
{
  printf("\n");
}

template<typename T0, typename T1, typename... ARGS>
  void get(int n, T0 t0, T1& t1, ARGS&&... args)
{
  std::cout << t0 << ":" " (" << n << "), ";
  t1 = n;
  get(n+1,std::forward<ARGS>(args)...);
}


template< typename T0 >
  unsigned fmt_data( char* buf, unsigned n, T0 t0 )
{
  return cw::toText(buf, n, t0);
}

template<>
  unsigned fmt_data( char* buf, unsigned n, const char* v )
{
  return cw::toText(buf,n,v);
}

unsigned to_text_base(char*, unsigned n, unsigned i )
{ return i; }

template<typename T0, typename T1, typename... ARGS>
  unsigned to_text_base( char* buf, unsigned  n, unsigned i, T0 t0, T1 t1, ARGS&&... args)
{
  i += fmt_data(buf+i, n-i, t0);
  i += fmt_data(buf+i, n-i, t1);
  
  if( i >= n )
    return i;

  return to_text_base(buf,n,i,std::forward<ARGS>(args)...);
}

template< typename... ARGS>
  unsigned to_text(const char* prefix, char* buf, unsigned  n, ARGS&&... args)
{
  unsigned i = cw::toText(buf, n, prefix );

  return to_text_base(buf,n,i,std::forward<ARGS>(args)...);
}



using namespace std;

enum { kIsFilePathFl = 0x01, kIsDirPathFl=0x02, kPathMustExistFl=0x04, kVarOptionalFl=0x08, kCreateDirFl=0x010 };
char* instantiatePathVariable( const cw::object_t* args, const char* label, unsigned flags )
{
  cw::rc_t    rc;
  const char* fn         = nullptr;
  char*       expandedFn = nullptr;

  // locate the cfg field associated with 'label'
  if((rc = args->get(label,fn)) != cw::kOkRC )
  {
    if( !cwIsFlag(flags,kVarOptionalFl) )
    {
      rc = cwLogError(cw::kLabelNotFoundRC,"The mandatory file '%s' was not found.",cwStringNullGuard(label));
      goto errLabel;
    }
    
    return nullptr;
  }

  // expand the path (replace ~ with home directory)
  if((expandedFn  = cw::filesys::expandPath(fn)) == nullptr )
  {
    rc = cwLogError(cw::kOpFailRC,"Path expansion failed on '%s'.",fn);
    goto errLabel;
  }

  // check if the path must exist
  if( cwIsFlag(flags,kPathMustExistFl) )
  {
    // if this is a file then the file must exist
    if( cwIsFlag(flags,kIsFilePathFl) && !cw::filesys::isFile(expandedFn) )
    {
      rc = cwLogError(cw::kFileNotFoundRC,"The path variable '%s' ('%s') does not identify an existing file.",label,expandedFn );
      goto errLabel;
    }

    // if this is a directory then the directory must exist
    if( cwIsFlag(flags,kIsDirPathFl ) && !cw::filesys::isDir(expandedFn))
    {

      // the dir. doesn't exist - is it ok to create it?
      if( cwIsFlag(flags,kCreateDirFl) )
      {
        if((rc = cw::filesys::makeDir( expandedFn)) != cw::kOkRC )
        {
          rc = cwLogError(rc,"Unable to create the directory for '%s' ('%s').",label,expandedFn);
          goto errLabel;
        }
        
      }
      else
      {    
        rc = cwLogError(cw::kFileNotFoundRC,"The path variable '%s' ('%s') does not identify an existing directory.",label,expandedFn );
        goto errLabel;
      }
    }
  }

  errLabel:
  if( rc != cw::kOkRC )
    cw::mem::release(expandedFn);

  return expandedFn;
}

char* requiredExistingDir( const cw::object_t* args, const char* label )
{ return instantiatePathVariable(args,label,kIsDirPathFl | kPathMustExistFl); }

char* optionalExistingDir( const cw::object_t* args, const char* label )
{ return instantiatePathVariable(args,label,kVarOptionalFl | kIsDirPathFl | kPathMustExistFl); }

char* requiredNewDir( const cw::object_t* args, const char* label )
{ return instantiatePathVariable(args,label,kIsDirPathFl | kPathMustExistFl | kCreateDirFl); }

char* optionalNewDir( const cw::object_t* args, const char* label )
{ return instantiatePathVariable(args,label,kVarOptionalFl | kIsDirPathFl | kPathMustExistFl | kCreateDirFl ); }

char* requiredExistingFile( const cw::object_t* args, const char* label )
{ return instantiatePathVariable(args,label,kIsFilePathFl | kPathMustExistFl); }

char* optionalExistingFile( const cw::object_t* args, const char* label )
{ return instantiatePathVariable(args,label,kVarOptionalFl | kIsFilePathFl | kPathMustExistFl); }

char* requiredNewFile( const cw::object_t* args, const char* label )
{ return instantiatePathVariable(args,label,0); }

char* optionalNewFile( const cw::object_t* args, const char* label )
{ return instantiatePathVariable(args,label,kVarOptionalFl); }


cw::rc_t variadicTplTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  print("a", 1, "b", 3.14, "c",5L);
  
  int v0=0,v1=0,v2=0;
  get(0, "a", v0, "b", v1, "c", v2);
  printf("get: %i %i %i",v0,v1,v2);
  
  printf("\n");

  const int bufN = 32;
  char buf[bufN];
  buf[0] = '\0';
  unsigned n = to_text("prefix: ",buf,bufN,"a",1,"b",3.2,"hi","ho");
  printf("%i : %s\n",n,buf);


  unsigned m = calc(0,1,2,3);
  printf("Calc:%i\n",m);

  return cw::kOkRC;
}



cw::rc_t fileSysTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  cw::filesys::pathPart_t* pp = cw::filesys::pathParts(__FILE__);
  
  cwLogInfo("dir:%s",pp->dirStr);
  cwLogInfo("fn: %s",pp->fnStr);
  cwLogInfo("ext:%s",pp->extStr);

  char* fn = cw::filesys::makeFn( pp->dirStr, pp->fnStr, pp->extStr, nullptr );

  cwLogInfo("fn: %s",fn);

  cw::mem::release(pp);
  cw::mem::release(fn);


  const char myPath[] = "~/src/foo";

  char* expPath = cw::filesys::expandPath(myPath);

  cwLogInfo("%s %s",myPath,expPath);

  cw::mem::release(expPath);
  
  return cw::kOkRC;
}

cw::rc_t numbCvtTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  int8_t x0 = 3;
  int x1 = 127;
  
  cw::numeric_convert( x1, x0 );
  printf("%i %i\n",x0,x1);
    

  int v0;
  double v1;
  cw::string_to_number("123",v0);
  cw::string_to_number("3.4",v1);
  printf("%i %f\n",v0,v1 );

  return cw::kOkRC;
}

cw::rc_t objectTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  cw::object_t* o;
  const char s [] = "{ a:1, b:2, c:[ 1.23, 4.56 ], d:true, e:false, f:true }";
  cw::objectFromString(s,o);

  int v;
  o->get("b",v);
  printf("value:%i\n",v);
  
  o->print();

  int a = 0;
  int b = 0;

  o->getv("a",a,"b",b);
  printf("G: %i %i\n",a,b);

  const unsigned bufN = 128;
  char buf[bufN];

  unsigned i = o->to_string(buf,bufN);
  printf("%i : %s\n",i, buf);
  
  cw::object_t* oo = o->duplicate();

  oo->print();
  
  oo->free();
  
    
  o->free();
  return cw::kOkRC;
}

cw::rc_t timeTest(             const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::time::test(); }
cw::rc_t threadTest(           const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::threadTest(); }
cw::rc_t spscBuf(              const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::spsc_buf::test(); }
cw::rc_t spscQueueTmpl(        const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::testSpScQueueTmpl(); }
cw::rc_t serialPortSrvTest(    const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::serialPortSrvTest(); }
cw::rc_t textBufTest(          const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::textBuf::test(); }
cw::rc_t audioBufTest(         const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::audio::buf::test(); }
cw::rc_t mtxTest(              const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::mtx::test(args); }
cw::rc_t audioFileTest(        const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::audiofile::test(args); }
cw::rc_t audioFileOp(          const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::afop::test(args); }
cw::rc_t audioFileMix(         const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::afop::mix(args); }
cw::rc_t audioFileSelToFile(   const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::afop::selectToFile(args); }
cw::rc_t audioFileCutAndMix(   const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::afop::cutAndMix(args); }
cw::rc_t audioFileParallelMix( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::afop::parallelMix(args); }
cw::rc_t audioFileTransformApp(const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::afop::transformApp(args); }
cw::rc_t audioFileConvolve(    const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::afop::convolve(args); }
cw::rc_t fftTest(              const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::dsp::fft::test(); }
cw::rc_t ifftTest(             const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::dsp::ifft::test(); }
cw::rc_t convolveTest(         const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::dsp::convolve::test(); }
cw::rc_t socketMdnsTest(       const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::net::mdns::test(); }
cw::rc_t dnsSdTest(            const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::net::dnssd::test(); }
cw::rc_t euConTest(            const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::eucon::test(); }

#if defined(cwWEBSOCK)
cw::rc_t websockSrvTest(    const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::websockSrvTest(); }
cw::rc_t ioTest(            const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::io::test(); }
cw::rc_t uiTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )         { return cw::ui::test(); }
#else
cw::rc_t _no_websock() { return cwLogError(cw::kResourceNotAvailableRC,"Websocket functionality not included in this build."); } 
cw::rc_t websockSrvTest(    const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return _no_websock(); }
cw::rc_t ioTest(            const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return _no_websock(); }
cw::rc_t uiTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )         { return _no_websock(); }
#endif


#if defined(cwALSA)
cw::rc_t midiDeviceTest(       const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::midi::device::test();}
cw::rc_t audioDevTest(         const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::audio::device::test( argc, argv ); }
cw::rc_t audioDevAlsaTest(     const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::audio::device::alsa::report(); }
cw::rc_t audioDevRpt(          const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return cw::audio::device::report(); }
#else
cw::rc_t _no_alsa() { return cwLogError(cw::kResourceNotAvailableRC,"ALSA based functionality not included in this build."); } 
cw::rc_t midiDeviceTest(       const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return _no_alsa();}
cw::rc_t audioDevTest(         const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return _no_alsa(); }
cw::rc_t audioDevAlsaTest(     const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return _no_alsa(); }
cw::rc_t audioDevRpt(          const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] ) { return _no_alsa(); }
#endif

cw::rc_t socketTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  cw::rc_t rc = cw::kOkRC;
  
  if( argc < 3 )
    rc = cwLogError(cw::kInvalidArgRC,"Invalid arg count to socketTest().");
  else
  {
    unsigned short localPort  = atoi(argv[1]);
    unsigned short remotePort = atoi(argv[2]);
    const char* remoteAddr = "127.0.0.1"; //"224.0.0.251"; //"127.0.0.1";
    printf("local:%i remote:%i\n", localPort, remotePort);
    
    rc = cw::net::socket::test( localPort, remoteAddr, remotePort );
  }
  return rc;
}

cw::rc_t socketTestTcp( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  // server: ./cw_rt main.cfg socketTcp 5434 5435 dgram/stream server
  // client: ./cw_rt main.cfg socketTcp 5435 5434 dgram/stream
  cw::rc_t rc = cw::kOkRC;
  
  if( argc < 4 )
    rc = cwLogError(cw::kInvalidArgRC,"Invalid arg. count to socketTestTcp().");
  else
  {
    unsigned short localPort  = atoi(argv[1]);
    unsigned short remotePort = atoi(argv[2]);
    bool           dgramFl    = strcmp(argv[3],"dgram") == 0;
    bool           serverFl   = false;
    
    if( argc >= 5 )
      serverFl = strcmp(argv[4],"server") == 0;

    printf("local:%i remote:%i %s %s\n", localPort, remotePort, dgramFl ? "dgram":"stream", serverFl?"server":"client");
    
    rc = cw::net::socket::test_tcp( localPort, "127.0.0.1", remotePort, dgramFl, serverFl );
  }

  return rc;
}

cw::rc_t socketSrvUdpTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  cw::rc_t rc = cw::kOkRC;
  
  if( argc < 4 )
    rc = cwLogError(cw::kInvalidArgRC,"Invalid arg. count to socketSrvUdpTest().");
  else
  {
    unsigned short localPort  = atoi(argv[1]);
    const char*    remoteIp   = argv[2];
    unsigned short remotePort = atoi(argv[3]);

    printf("local:%i to remote:%s %i\n", localPort, remoteIp, remotePort);
    
    rc = cw::net::srv::test_udp_srv( localPort, remoteIp, remotePort );
  }
  return rc;
}
cw::rc_t socketSrvTcpTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  cw::rc_t rc = cw::kOkRC;
  
  if( argc < 4 )
    rc = cwLogError(cw::kInvalidArgRC,"Invaid arg. count to socketSrvTcpTest().");
  else
  {
    unsigned short localPort  = atoi(argv[1]);
    const char*    remoteIp   = argv[2];
    unsigned short remotePort = atoi(argv[3]);

    printf("local:%i to remote:%s %i\n", localPort, remoteIp, remotePort);
    
    rc = cw::net::srv::test_tcp_srv( localPort, remoteIp, remotePort );
  }
  return rc;
}

cw::rc_t sockMgrTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  cw::rc_t       rc          = cw::kOkRC;
  bool           tcpFl       = false;
  const char*    localNicDev = nullptr;
  unsigned short localPort   = 0;
  const char*    remoteIp    = nullptr;
  unsigned short remotePort  = 0;
  int argi = 0;
  
  if( argc <3 )
  {
    rc = cwLogError(cw::kInvalidArgRC,"Error: Invalid argument count to sockMgrTest().");
    goto errLabel;
  }

  // The first arg. must be 'tcp' or 'udp'.
  if( strcmp(argv[1],"tcp")!=0 && strcmp(argv[1],"udp")!=0 )
  {
    rc = cwLogError(cw::kInvalidArgRC,"sockMgrTest() Error: The first argument must be 'udp' or 'tcp'\n");
    goto errLabel;
  }

   
  tcpFl  = strcmp(argv[1],"tcp")==0;
 
  argi = 2;

  // If the next token is 'dev' ...
  if( strcmp(argv[argi++],"dev") == 0 )
  {
    if( argc <= argi )
    {
      rc = cwLogError(cw::kInvalidArgRC,"sockMgrTest() Error: No local NIC given.\n");
      goto errLabel;
    }

    // .. then the next arg is the localNicDev
    localNicDev = argv[argi++];
  }

  if( argc <= argi )
  {
    rc = cwLogError(cw::kInvalidArgRC,"sockMgrTest() Error: No local port was given.\n");
    goto errLabel;
  }

  // get the local port
  localPort = atoi(argv[argi++]);
  
  if( argc > argi)
  {
    remoteIp   = argv[argi++];

    if( argc > argi)
      remotePort = atoi(argv[argi++]);
  }
  
  
  if( remoteIp != nullptr && remotePort == 0 )
  {
    rc = cwLogError(cw::kInvalidArgRC,"sockMgrTest() Error: A remote adddress '%s' was given but no remote port was given.", remoteIp);
    goto errLabel;
  }

  cwLogInfo("style:%s local:%i to remote:%s %i\n", argv[1], localPort, cwStringNullGuard(remoteIp), remotePort);      

  rc = cw::socksrv::testMain( tcpFl, localNicDev, localPort, remoteIp, remotePort  );

  return rc;
    
  errLabel:

  rc = cwLogError(rc,"SockMgrTest() failed.");
  
  //                                                1                                 2               3          4
  //                                                1         2         3             4               5          6
  cwLogInfo("Usage: ./cwtest <cfg_fn> sockMgrTest 'udp | tcp' {'dev' <localNicDevice>} <localPort>  { <remote_ip> <remote_port> }\n");
  
  return rc;
}

cw::rc_t mnistTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  char* inDir  = requiredExistingDir( args, "inDir");
  char* htmlFn = requiredNewFile(     args, "outHtmlFn");
  
  return cw::dataset::mnist::test(inDir,htmlFn);
}

cw::rc_t datasetTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{ return cw::dataset::test(args); }

cw::rc_t svgTest(   const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  char* htmlFn = requiredNewFile( args, "outHtmlFn");
  char* cssFn  = optionalNewFile( args, "outCssFn");
  
  cw::rc_t rc = cw::svg::test(htmlFn,cssFn);
  
  cw::mem::release(htmlFn);
  cw::mem::release(cssFn);
  return rc;
}

cw::rc_t dirEntryTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  cw::rc_t rc = cw::kOkRC;
  if( argc < 2 )
    rc = cwLogError(cw::kInvalidArgRC,"dirEntryTest() error: Invalid arg. count.");
  else
  {
    const char*              path         = argv[1];
    unsigned                 dirEntryN    = 0;
    unsigned                 includeFlags = cw::filesys::kFileFsFl | cw::filesys::kDirFsFl | cw::filesys::kFullPathFsFl | cw::filesys::kRecurseFsFl;
    cw::filesys::dirEntry_t* de           = cw::filesys::dirEntries( path,includeFlags, &dirEntryN );
    for(unsigned i=0; i<dirEntryN; ++i)
      cwLogInfo("%s",de[i].name);

    cw::mem::release(de);
  }
  return rc;
}

cw::rc_t stubTest( const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] )
{
  cw::rc_t rc = cw::kOkRC;
  return rc;
}

const cw::object_t* _locateArgsRecd( const cw::object_t* cfg, const char*& cfgLabel )
{
  const cw::object_t* o;

  if((cfg = cfg->find_child("test")) == nullptr )
  {
    cwLogError(cw::kSyntaxErrorRC,"The cwtest cfg. file does not have a 'test' record.");
    return nullptr;
  }

  if((o = cfg->find_child(cfgLabel)) == nullptr )
      cwLogError(cw::kLabelNotFoundRC,"The test selector: '%s' was not found in the configuration file.", cwStringNullGuard(cfgLabel));
  else
  {
  
    const struct cw::object_str* oo     = nullptr;

    // if the cfg record label does not match the test mode label - then get the test mode label
    if((oo = o->find_child( "test_label" )) != nullptr )
    {
      const char* test_label = nullptr;
      if( oo->value(test_label) == cw::kOkRC )
        cfgLabel = test_label;
    }
  }

  return o;
}

int main( int argc, const char* argv[] )
{  
  cw::rc_t rc = cw::kOkRC;
  
  typedef struct func_str
  {
    const char* label;
    cw::rc_t (*func)(const cw::object_t* cfg, const cw::object_t* args, int argc, const char* argv[] );    
  } func_t;

  // function dispatch list
  func_t modeArray[] =
  {
   { "variadicTpl", variadicTplTest },
   { "fileSys", fileSysTest },
   { "numbCvt", numbCvtTest },
   { "object", objectTest },
   { "time", timeTest },
   { "thread", threadTest },
   { "spscBuf", spscBuf },
   { "spscQueueTmpl", spscQueueTmpl },
   { "websockSrv", websockSrvTest },
   { "serialSrv", serialPortSrvTest },
   { "midiDevice", midiDeviceTest },
   { "textBuf", textBufTest },
   { "audioBuf", audioBufTest },
   { "audioDev",audioDevTest },
   { "audioDevAlsa", audioDevAlsaTest },
   { "audioDevRpt", audioDevRpt },
   //{ "nbmem", nbmemTest },
   { "socket", socketTest },
   { "socketTcp", socketTestTcp },
   { "socketSrvUdp", socketSrvUdpTest },
   { "socketSrvTcp", socketSrvTcpTest },
   { "sockMgrTest", sockMgrTest },
   { "uiTest", uiTest },
   { "socketMdns", socketMdnsTest },
   { "dnssd",  dnsSdTest },
   { "eucon",  euConTest },
   { "dirEntry", dirEntryTest },
   { "io", ioTest },
   { "mnist", mnistTest },
   { "dataset", datasetTest },
   { "svg",   svgTest },
   { "mtx",   mtxTest },
   { "afop",      audioFileOp },
   { "audiofile", audioFileTest },
   { "audio_mix", audioFileMix },
   { "select_to_file", audioFileSelToFile },
   { "cut_and_mix", audioFileCutAndMix },
   { "parallel_mix",audioFileParallelMix },
   { "transform_app", audioFileTransformApp },
   { "convolve_file", audioFileConvolve },
   { "fft", fftTest },
   { "ifft", ifftTest },
   { "convolve", convolveTest },
   { "stub", stubTest },
   { nullptr, nullptr }
  };

  // read the command line
        cw::object_t* cfg   = nullptr;
  const char*         cfgFn = argc > 1 ? argv[1] : nullptr;
  const char*         mode  = argc > 2 ? argv[2] : nullptr;

  
  cw::log::createGlobal();

  // if valid command line args were given and the cfg file was successfully read
  if( cfgFn != nullptr && mode != nullptr && objectFromFile( cfgFn, cfg ) == cw::kOkRC )
  {

    const cw::object_t* args;
    int  i = 0;
  
    // if the arg's record was not found
    if((args = _locateArgsRecd(cfg,mode)) == nullptr )
      goto errLabel;
  
    // locate the requested function and call it
    for(i=0; modeArray[i].label!=nullptr; ++i)
    {
      if( cw::textCompare(modeArray[i].label,mode)==0 )
      {
        rc = modeArray[i].func( cfg, args, argc-2, argv + 2 );
        break;
      }
    }
  
    // if the requested function was not found
    if( modeArray[i].label == nullptr )
      rc = cwLogError(cw::kInvalidArgRC,"The mode selector: '%s' is not valid.", cwStringNullGuard(mode));
    
  errLabel:
    if( cfg != nullptr )
      cfg->free();
  }
  
  cw::log::destroyGlobal();

  return (int)rc;
}


  


