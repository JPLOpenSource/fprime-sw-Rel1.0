// ====================================================================== 
// \title  ZmqPubImpl.cpp
// \author tcanham
// \brief  cpp file for ZmqPub component implementation class
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


#include <fprime-zmq/zmq-pub/ZmqPubComponentImpl.hpp>
#include <Fw/Types/BasicTypes.hpp>
#include <Fw/Types/EightyCharString.hpp>
#include <Os/Task.hpp>
#include <errno.h>
#include <string.h>

#define DEBUG_PRINT(x,...) printf(x,##__VA_ARGS__)
//#define DEBUG_PRINT(x,...)

namespace Zmq {

  // ----------------------------------------------------------------------
  // Construction, initialization, and destruction 
  // ----------------------------------------------------------------------

  ZmqPubComponentImpl ::
#if FW_OBJECT_NAMES == 1
    ZmqPubComponentImpl(
        const char *const compName
    ) :
      ZmqPubComponentBase(compName)
#else
    ZmqPubImpl(void)
#endif
    ,m_context(0)
  {

  }

  void ZmqPubComponentImpl ::
    init(
      NATIVE_INT_TYPE queueDepth, /*!< The queue depth*/
      NATIVE_INT_TYPE msgSize, /*!< The message size*/
      NATIVE_INT_TYPE instance /*!< The instance number*/
   ) {
    ZmqPubComponentBase::init(queueDepth, msgSize, instance);
  }

  ZmqPubComponentImpl ::
    ~ZmqPubComponentImpl(void)
  {

      // clean up zmq state
      zmq_ctx_destroy (this->m_context);
  }

  // ----------------------------------------------------------------------
  // Handler implementations for user-defined typed input ports
  // ----------------------------------------------------------------------

  void ZmqPubComponentImpl ::
    Sched_handler(
        const NATIVE_INT_TYPE portNum,
        NATIVE_UINT_TYPE context
    )
  {
    // TODO
  }

  void ZmqPubComponentImpl::preamble(void) {

      // ZMQ requires that a socket be created, used, and destroyed on the same thread,
      // so we create it in the preamble
      this->m_pubSocket = zmq_socket (this->m_context, ZMQ_PUB);
  }

  void ZmqPubComponentImpl::finalizer(void) {

      // ZMQ requires that a socket be created, used, and destroyed on the same thread,
      // so we close it in the finalizer
      DEBUG_PRINT("Finalizing\n");
      zmq_close(this->m_pubSocket);
  }

  // ----------------------------------------------------------------------
  // Handler implementations for user-defined serial input ports
  // ----------------------------------------------------------------------

  void ZmqPubComponentImpl ::
    PortsIn_handler(
        NATIVE_INT_TYPE portNum, /*!< The port number*/
        Fw::SerializeBufferBase &Buffer /*!< The serialization buffer*/
    )
  {
      DEBUG_PRINT("PortsIn_handler: %d\n",portNum);
      Fw::SerializeStatus stat;
      m_sendBuff.resetSer();

      // serialize port call
      stat = m_sendBuff.serialize(portNum);
      FW_ASSERT(Fw::FW_SERIALIZE_OK == stat,stat);
      stat = m_sendBuff.serialize(Buffer);
      FW_ASSERT(Fw::FW_SERIALIZE_OK == stat,stat);
      // send on zmq socket
      bool done = false;
      while (not done) {
          int zstat = zmq_send(this->m_pubSocket,m_sendBuff.getBuffAddr(),m_sendBuff.getBuffLength(),0);
          if (-1 == zstat) {
              if (this->zmqError("port zmq_send")) {
                  done = true;
              }
          } else {
              FW_ASSERT((int)m_sendBuff.getBuffLength() == zstat,zstat);
              done = true;
          }
      }

  }

  void ZmqPubComponentImpl::open(
          const char* port /*!< port for connection, client or server */
          ) {

      // store values for worker thread
      strncpy(this->m_port,port,ZMQ_PUB_ENDPOINT_NAME_SIZE);
      this->m_port[ZMQ_PUB_ENDPOINT_NAME_SIZE-1] = 0;

      // create zmq context
      this->m_context = zmq_ctx_new ();
      FW_ASSERT(this->m_context);

  }

  bool ZmqPubComponentImpl::zmqError(const char* from) {
      switch (zmq_errno()) {
          case ETERM:
              DEBUG_PRINT("%s: ZMQ terminate\n",from);
              return true;
          case EINTR:
              DEBUG_PRINT("%s: ZMQ EINTR\n",from);
              return false;
          default:
              DEBUG_PRINT("%s: ZMQ error: %s\n",from,zmq_strerror(zmq_errno()));
              return true;
      }
  }

#ifdef BUILD_UT
  void ZmqPubComponentImpl::ZmqSerialBuffer::operator=(const ZmqSerialBuffer& other) {
      this->resetSer();
      this->serialize(other.getBuffAddr(),other.getBuffLength(),true);
  }

  ZmqPubComponentImpl::ZmqSerialBuffer::ZmqSerialBuffer(
          const Fw::SerializeBufferBase& other) : Fw::SerializeBufferBase() {
      FW_ASSERT(sizeof(this->m_buff)>= other.getBuffLength(),sizeof(this->m_buff),other.getBuffLength());
      memcpy(this->m_buff,other.getBuffAddr(),other.getBuffLength());
      this->setBuffLen(other.getBuffLength());
  }

  ZmqPubComponentImpl::ZmqSerialBuffer::ZmqSerialBuffer(
          const ZmqPubComponentImpl::ZmqSerialBuffer& other) : Fw::SerializeBufferBase() {
      FW_ASSERT(sizeof(this->m_buff)>= other.getBuffLength(),sizeof(this->m_buff),other.getBuffLength());
      memcpy(this->m_buff,other.m_buff,other.getBuffLength());
      this->setBuffLen(other.getBuffLength());
  }

  ZmqPubComponentImpl::ZmqSerialBuffer::ZmqSerialBuffer(): Fw::SerializeBufferBase() {

  }

#endif


} // end namespace Zmq
