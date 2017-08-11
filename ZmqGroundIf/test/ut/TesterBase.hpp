// ======================================================================
// \title  ZmqGroundIf/test/ut/TesterBase.hpp
// \author Auto-generated
// \brief  hpp file for ZmqGroundIf component test harness base class
//
// \copyright
// Copyright 2009-2015, by the California Institute of Technology.
// ALL RIGHTS RESERVED.  United States Government Sponsorship
// acknowledged. Any commercial use must be negotiated with the Office
// of Technology Transfer at the California Institute of Technology.
//
// This software may be subject to U.S. export control laws and
// regulations.  By accepting this document, the user agrees to comply
// with all U.S. export laws and regulations.  User has the
// responsibility to obtain export licenses, or other export authority
// as may be required before exporting such information to foreign
// countries or providing access to foreign persons.
// ======================================================================

#ifndef ZmqGroundIf_TESTER_BASE_HPP
#define ZmqGroundIf_TESTER_BASE_HPP

#include <fprime-zmq/ZmqGroundIf/ZmqGroundIfComponentAc.hpp>
#include <Fw/Types/Assert.hpp>
#include <Fw/Comp/PassiveComponentBase.hpp>
#include <stdio.h>
#include <Fw/Port/InputSerializePort.hpp>

namespace Zmq {

  //! \class ZmqGroundIfTesterBase
  //! \brief Auto-generated base class for ZmqGroundIf component test harness
  //!
  class ZmqGroundIfTesterBase :
    public Fw::PassiveComponentBase
  {

    public:

      // ----------------------------------------------------------------------
      // Initialization
      // ----------------------------------------------------------------------

      //! Initialize object ZmqGroundIfTesterBase
      //!
      virtual void init(
          const NATIVE_INT_TYPE instance = 0 /*!< The instance number*/
      );

    public:

      // ----------------------------------------------------------------------
      // Connectors for 'to' ports
      // Connect these output ports to the input ports under test
      // ----------------------------------------------------------------------

      //! Connect downlinkPort to to_downlinkPort[portNum]
      //!
      void connect_to_downlinkPort(
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::InputComPort *const downlinkPort /*!< The port*/
      );

      //! Connect fileDownlinkBufferSendIn to to_fileDownlinkBufferSendIn[portNum]
      //!
      void connect_to_fileDownlinkBufferSendIn(
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::InputBufferSendPort *const fileDownlinkBufferSendIn /*!< The port*/
      );

    public:

      // ----------------------------------------------------------------------
      // Getters for 'from' ports
      // Connect these input ports to the output ports under test
      // ----------------------------------------------------------------------

      //! Get the port that receives input from fileUplinkBufferSendOut
      //!
      //! \return from_fileUplinkBufferSendOut[portNum]
      //!
      Fw::InputBufferSendPort* get_from_fileUplinkBufferSendOut(
          const NATIVE_INT_TYPE portNum /*!< The port number*/
      );

      //! Get the port that receives input from Log
      //!
      //! \return from_Log[portNum]
      //!
      Fw::InputLogPort* get_from_Log(
          const NATIVE_INT_TYPE portNum /*!< The port number*/
      );

#if FW_ENABLE_TEXT_LOGGING == 1
      //! Get the port that receives input from LogText
      //!
      //! \return from_LogText[portNum]
      //!
      Fw::InputLogTextPort* get_from_LogText(
          const NATIVE_INT_TYPE portNum /*!< The port number*/
      );
#endif

      //! Get the port that receives input from Time
      //!
      //! \return from_Time[portNum]
      //!
      Fw::InputTimePort* get_from_Time(
          const NATIVE_INT_TYPE portNum /*!< The port number*/
      );

      //! Get the port that receives input from uplinkPort
      //!
      //! \return from_uplinkPort[portNum]
      //!
      Fw::InputComPort* get_from_uplinkPort(
          const NATIVE_INT_TYPE portNum /*!< The port number*/
      );

      //! Get the port that receives input from fileDownlinkBufferSendOut
      //!
      //! \return from_fileDownlinkBufferSendOut[portNum]
      //!
      Fw::InputBufferSendPort* get_from_fileDownlinkBufferSendOut(
          const NATIVE_INT_TYPE portNum /*!< The port number*/
      );

      //! Get the port that receives input from fileUplinkBufferGet
      //!
      //! \return from_fileUplinkBufferGet[portNum]
      //!
      Fw::InputBufferGetPort* get_from_fileUplinkBufferGet(
          const NATIVE_INT_TYPE portNum /*!< The port number*/
      );

    protected:

      // ----------------------------------------------------------------------
      // Construction and destruction
      // ----------------------------------------------------------------------

      //! Construct object ZmqGroundIfTesterBase
      //!
      ZmqGroundIfTesterBase(
#if FW_OBJECT_NAMES == 1
          const char *const compName, /*!< The component name*/
          const U32 maxHistorySize /*!< The maximum size of each history*/
#else
          const U32 maxHistorySize /*!< The maximum size of each history*/
#endif
      );

      //! Destroy object ZmqGroundIfTesterBase
      //!
      virtual ~ZmqGroundIfTesterBase(void);

      // ----------------------------------------------------------------------
      // Test history
      // ----------------------------------------------------------------------

    protected:

      //! \class History
      //! \brief A history of port inputs
      //!
      template <typename T> class History {

        public:

          //! Create a History
          //!
          History(
              const U32 maxSize /*!< The maximum history size*/
          ) : 
              numEntries(0), 
              maxSize(maxSize) 
          { 
            this->entries = new T[maxSize];
          }

          //! Destroy a History
          //!
          ~History() {
            delete[] this->entries;
          }

          //! Clear the history
          //!
          void clear() { this->numEntries = 0; }

          //! Push an item onto the history
          //!
          void push_back(
              T entry /*!< The item*/
          ) {
            FW_ASSERT(this->numEntries < this->maxSize);
            entries[this->numEntries++] = entry;
          }

          //! Get an item at an index
          //!
          //! \return The item at index i
          //!
          T at(
              const U32 i /*!< The index*/
          ) const {
            FW_ASSERT(i < this->numEntries);
            return entries[i];
          }

          //! Get the number of entries in the history
          //!
          //! \return The number of entries in the history
          //!
          U32 size(void) const { return this->numEntries; }

        private:

          //! The number of entries in the history
          //!
          U32 numEntries;

          //! The maximum history size
          //!
          const U32 maxSize;

          //! The entries
          //!
          T *entries;

      };

      //! Clear all history
      //!
      void clearHistory(void);

    protected:

      // ----------------------------------------------------------------------
      // Handler prototypes for typed from ports
      // ----------------------------------------------------------------------

      //! Handler prototype for from_fileUplinkBufferSendOut
      //!
      virtual void from_fileUplinkBufferSendOut_handler(
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::Buffer fwBuffer 
      ) = 0;

      //! Handler base function for from_fileUplinkBufferSendOut
      //!
      void from_fileUplinkBufferSendOut_handlerBase(
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::Buffer fwBuffer 
      );

      //! Handler prototype for from_uplinkPort
      //!
      virtual void from_uplinkPort_handler(
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::ComBuffer &data, /*!< Buffer containing packet data*/
          U32 context /*!< Call context value; meaning chosen by user*/
      ) = 0;

      //! Handler base function for from_uplinkPort
      //!
      void from_uplinkPort_handlerBase(
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::ComBuffer &data, /*!< Buffer containing packet data*/
          U32 context /*!< Call context value; meaning chosen by user*/
      );

      //! Handler prototype for from_fileDownlinkBufferSendOut
      //!
      virtual void from_fileDownlinkBufferSendOut_handler(
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::Buffer fwBuffer 
      ) = 0;

      //! Handler base function for from_fileDownlinkBufferSendOut
      //!
      void from_fileDownlinkBufferSendOut_handlerBase(
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::Buffer fwBuffer 
      );

      //! Handler prototype for from_fileUplinkBufferGet
      //!
      virtual Fw::Buffer from_fileUplinkBufferGet_handler(
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          U32 size 
      ) = 0;

      //! Handler base function for from_fileUplinkBufferGet
      //!
      Fw::Buffer from_fileUplinkBufferGet_handlerBase(
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          U32 size 
      );

    protected:

      // ----------------------------------------------------------------------
      // Histories for typed from ports
      // ----------------------------------------------------------------------

      //! Clear from port history
      //!
      void clearFromPortHistory(void);

      //! The total number of from port entries
      //!
      U32 fromPortHistorySize;

      //! Push an entry on the history for from_fileUplinkBufferSendOut
      void pushFromPortEntry_fileUplinkBufferSendOut(
          Fw::Buffer fwBuffer 
      );

      //! A history entry for from_fileUplinkBufferSendOut
      //!
      typedef struct {
        Fw::Buffer fwBuffer;
      } FromPortEntry_fileUplinkBufferSendOut;

      //! The history for from_fileUplinkBufferSendOut
      //!
      History<FromPortEntry_fileUplinkBufferSendOut> 
        *fromPortHistory_fileUplinkBufferSendOut;

      //! Push an entry on the history for from_uplinkPort
      void pushFromPortEntry_uplinkPort(
          Fw::ComBuffer &data, /*!< Buffer containing packet data*/
          U32 context /*!< Call context value; meaning chosen by user*/
      );

      //! A history entry for from_uplinkPort
      //!
      typedef struct {
        Fw::ComBuffer data;
        U32 context;
      } FromPortEntry_uplinkPort;

      //! The history for from_uplinkPort
      //!
      History<FromPortEntry_uplinkPort> 
        *fromPortHistory_uplinkPort;

      //! Push an entry on the history for from_fileDownlinkBufferSendOut
      void pushFromPortEntry_fileDownlinkBufferSendOut(
          Fw::Buffer fwBuffer 
      );

      //! A history entry for from_fileDownlinkBufferSendOut
      //!
      typedef struct {
        Fw::Buffer fwBuffer;
      } FromPortEntry_fileDownlinkBufferSendOut;

      //! The history for from_fileDownlinkBufferSendOut
      //!
      History<FromPortEntry_fileDownlinkBufferSendOut> 
        *fromPortHistory_fileDownlinkBufferSendOut;

      //! Push an entry on the history for from_fileUplinkBufferGet
      void pushFromPortEntry_fileUplinkBufferGet(
          U32 size 
      );

      //! A history entry for from_fileUplinkBufferGet
      //!
      typedef struct {
        U32 size;
      } FromPortEntry_fileUplinkBufferGet;

      //! The history for from_fileUplinkBufferGet
      //!
      History<FromPortEntry_fileUplinkBufferGet> 
        *fromPortHistory_fileUplinkBufferGet;

    protected:

      // ----------------------------------------------------------------------
      // Invocation functions for to ports
      // ----------------------------------------------------------------------

      //! Invoke the to port connected to downlinkPort
      //!
      void invoke_to_downlinkPort(
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::ComBuffer &data, /*!< Buffer containing packet data*/
          U32 context /*!< Call context value; meaning chosen by user*/
      );

      //! Invoke the to port connected to fileDownlinkBufferSendIn
      //!
      void invoke_to_fileDownlinkBufferSendIn(
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::Buffer fwBuffer 
      );

    public:

      // ----------------------------------------------------------------------
      // Getters for port counts
      // ----------------------------------------------------------------------

      //! Get the number of from_fileUplinkBufferSendOut ports
      //!
      //! \return The number of from_fileUplinkBufferSendOut ports
      //!
      NATIVE_INT_TYPE getNum_from_fileUplinkBufferSendOut(void) const;

      //! Get the number of from_Log ports
      //!
      //! \return The number of from_Log ports
      //!
      NATIVE_INT_TYPE getNum_from_Log(void) const;

#if FW_ENABLE_TEXT_LOGGING == 1
      //! Get the number of from_LogText ports
      //!
      //! \return The number of from_LogText ports
      //!
      NATIVE_INT_TYPE getNum_from_LogText(void) const;
#endif

      //! Get the number of to_downlinkPort ports
      //!
      //! \return The number of to_downlinkPort ports
      //!
      NATIVE_INT_TYPE getNum_to_downlinkPort(void) const;

      //! Get the number of from_Time ports
      //!
      //! \return The number of from_Time ports
      //!
      NATIVE_INT_TYPE getNum_from_Time(void) const;

      //! Get the number of from_uplinkPort ports
      //!
      //! \return The number of from_uplinkPort ports
      //!
      NATIVE_INT_TYPE getNum_from_uplinkPort(void) const;

      //! Get the number of from_fileDownlinkBufferSendOut ports
      //!
      //! \return The number of from_fileDownlinkBufferSendOut ports
      //!
      NATIVE_INT_TYPE getNum_from_fileDownlinkBufferSendOut(void) const;

      //! Get the number of to_fileDownlinkBufferSendIn ports
      //!
      //! \return The number of to_fileDownlinkBufferSendIn ports
      //!
      NATIVE_INT_TYPE getNum_to_fileDownlinkBufferSendIn(void) const;

      //! Get the number of from_fileUplinkBufferGet ports
      //!
      //! \return The number of from_fileUplinkBufferGet ports
      //!
      NATIVE_INT_TYPE getNum_from_fileUplinkBufferGet(void) const;

    protected:

      // ----------------------------------------------------------------------
      // Connection status for to ports
      // ----------------------------------------------------------------------

      //! Check whether port is connected
      //!
      //! Whether to_downlinkPort[portNum] is connected
      //!
      bool isConnected_to_downlinkPort(
          const NATIVE_INT_TYPE portNum /*!< The port number*/
      );

      //! Check whether port is connected
      //!
      //! Whether to_fileDownlinkBufferSendIn[portNum] is connected
      //!
      bool isConnected_to_fileDownlinkBufferSendIn(
          const NATIVE_INT_TYPE portNum /*!< The port number*/
      );

    private:

      // ----------------------------------------------------------------------
      // To ports
      // ----------------------------------------------------------------------

      //! To port connected to downlinkPort
      //!
      Fw::OutputComPort m_to_downlinkPort[1];

      //! To port connected to fileDownlinkBufferSendIn
      //!
      Fw::OutputBufferSendPort m_to_fileDownlinkBufferSendIn[1];

    private:

      // ----------------------------------------------------------------------
      // From ports
      // ----------------------------------------------------------------------

      //! From port connected to fileUplinkBufferSendOut
      //!
      Fw::InputBufferSendPort m_from_fileUplinkBufferSendOut[1];

      //! From port connected to Log
      //!
      Fw::InputLogPort m_from_Log[1];

#if FW_ENABLE_TEXT_LOGGING == 1
      //! From port connected to LogText
      //!
      Fw::InputLogTextPort m_from_LogText[1];
#endif

      //! From port connected to Time
      //!
      Fw::InputTimePort m_from_Time[1];

      //! From port connected to uplinkPort
      //!
      Fw::InputComPort m_from_uplinkPort[1];

      //! From port connected to fileDownlinkBufferSendOut
      //!
      Fw::InputBufferSendPort m_from_fileDownlinkBufferSendOut[1];

      //! From port connected to fileUplinkBufferGet
      //!
      Fw::InputBufferGetPort m_from_fileUplinkBufferGet[1];

    private:

      // ----------------------------------------------------------------------
      // Static functions for output ports
      // ----------------------------------------------------------------------

      //! Static function for port from_fileUplinkBufferSendOut
      //!
      static void from_fileUplinkBufferSendOut_static(
          Fw::PassiveComponentBase *const callComp, /*!< The component instance*/
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::Buffer fwBuffer 
      );

      //! Static function for port from_Log
      //!
      static void from_Log_static(
          Fw::PassiveComponentBase *const callComp, /*!< The component instance*/
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          FwEventIdType id, /*!< Log ID*/
          Fw::Time &timeTag, /*!< Time Tag*/
          Fw::LogSeverity severity, /*!< The severity argument*/
          Fw::LogBuffer &args /*!< Buffer containing serialized log entry*/
      );

#if FW_ENABLE_TEXT_LOGGING == 1
      //! Static function for port from_LogText
      //!
      static void from_LogText_static(
          Fw::PassiveComponentBase *const callComp, /*!< The component instance*/
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          FwEventIdType id, /*!< Log ID*/
          Fw::Time &timeTag, /*!< Time Tag*/
          Fw::TextLogSeverity severity, /*!< The severity argument*/
          Fw::TextLogString &text /*!< Text of log message*/
      );
#endif

      //! Static function for port from_Time
      //!
      static void from_Time_static(
          Fw::PassiveComponentBase *const callComp, /*!< The component instance*/
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::Time &time /*!< The U32 cmd argument*/
      );

      //! Static function for port from_uplinkPort
      //!
      static void from_uplinkPort_static(
          Fw::PassiveComponentBase *const callComp, /*!< The component instance*/
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::ComBuffer &data, /*!< Buffer containing packet data*/
          U32 context /*!< Call context value; meaning chosen by user*/
      );

      //! Static function for port from_fileDownlinkBufferSendOut
      //!
      static void from_fileDownlinkBufferSendOut_static(
          Fw::PassiveComponentBase *const callComp, /*!< The component instance*/
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          Fw::Buffer fwBuffer 
      );

      //! Static function for port from_fileUplinkBufferGet
      //!
      static Fw::Buffer from_fileUplinkBufferGet_static(
          Fw::PassiveComponentBase *const callComp, /*!< The component instance*/
          const NATIVE_INT_TYPE portNum, /*!< The port number*/
          U32 size 
      );

  };

} // end namespace Zmq

#endif
