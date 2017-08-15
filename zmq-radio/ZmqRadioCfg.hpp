/*
 * ZmqRadioCfg.hpp
 *
 *  Created on: Aug 14, 2017
 *      Author: dkooi 
 */

#ifndef ZMQ_RADIOCFG_HPP
#define ZMQ_RADIOCFG_HPP

namespace Zmq{

    static const NATIVE_UINT_TYPE ZMQ_RADIO_ENDPOINT_NAME_SIZE = 256;
    static const NATIVE_UINT_TYPE ZMQ_RADIO_MSG_SIZE = 256;

    static const NATIVE_UINT_TYPE ZMQ_RADIO_LINGER = 0;
    static const NATIVE_UINT_TYPE ZMQ_RADIO_RCVTIMEO = 500; // ms
    static const NATIVE_UINT_TYPE ZMQ_RADIO_SNDTIMEO = 500; // ms

    static const NATIVE_UINT_TYPE ZMQ_RADIO_REG_MSG_SIZE = 3;
    static const NATIVE_UINT_TYPE ZMQ_RADIO_REG_RESP_MSG_SIZE = 3;

    /* Component States */
    static const U8 ZMQ_RADIO_RECONNECT_STATE            = 0x01;
    static const U8 ZMQ_RADIO_RECONNECT_TRANSITION_STATE = 0x02;
    static const U8 ZMQ_RADIO_CONNECTED_STATE            = 0x04;


}



#endif /* ZMQ_RADIOCFG_HPP */
