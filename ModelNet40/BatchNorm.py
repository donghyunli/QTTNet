# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 22:13:11 2018

@author: amax
"""

import tensorflow as tf
from tensorflow.python.training import moving_averages
from tensorflow.python.framework import ops
from Quantize import fbn_G,fbn_B,fbn_mean,fbn_var,fbn_x

def batch_normalization(x, mean, variance, offset, scale, epsilon):
    # Apply Quantized Batch Normalization
    mean=fbn_mean(mean)
    std=tf.sqrt(variance)
    std=fbn_var(std)+epsilon

    x = (x - mean) / std 
    x=fbn_x(x)

    if scale is not None:
      scale = fbn_G(scale)
      x = x * scale
    if offset is not None:
      offset = fbn_B(offset)
      x = x + offset
    return x

# BN for 2DCNN
def BatchNorm(x,center=True, scale=True, is_training=True, decay=0.9, epsilon=1./(2**15), Random=None, data_format=None):
  with tf.variable_scope('BatchNorm',reuse=tf.AUTO_REUSE):
    shape = x.get_shape().as_list()
    if data_format=='NCHW' and len(shape)==4:
      x = tf.transpose(x,[0,2,3,1]) # to NDHWC
      print('batch norma shape:', x.shape)
    reduce_axis = [0] if len(shape) == 2 else [0]

    channel = x.get_shape().as_list()[-1]
    if center:
        beta = tf.Variable(tf.constant(0.0,tf.float32,shape=[channel]),
        name='beta') 
    else:
        beta = None
    if scale:
        gamma = tf.Variable(tf.constant(1.0,tf.float32,shape=[channel]),
        name='gamma') 
    else:
        gamma = None


    moving_mean = tf.Variable(tf.constant(0.0,tf.float32,shape=[channel]),
      name='moving_mean', trainable=False)
    
    

    moving_variance = tf.Variable(tf.constant(1.0,tf.float32,shape=[channel]),
      name='moving_variance', trainable=False)
   
    if is_training:  
      
      mean, variance = tf.nn.moments(x, reduce_axis, name='moments')
      if Random is not None:
        mean = mean * tf.random_uniform([], minval=1.0-Random, maxval=1.0+Random)
        variance = variance * tf.random_uniform([], minval=1.0-Random, maxval=1.0+Random)
              
      update_mean = moving_averages.assign_moving_average(moving_mean, mean, decay, False)
      update_variance = moving_averages.assign_moving_average(moving_variance, variance, decay, False)
      ops.add_to_collections(ops.GraphKeys.UPDATE_OPS, update_mean)
      ops.add_to_collections(ops.GraphKeys.UPDATE_OPS, update_variance)

      x = batch_normalization(x, mean, variance, beta, gamma, epsilon)
    else:
      x = batch_normalization(x, moving_mean, moving_variance, beta , gamma , epsilon)

    if data_format == 'NCHW' and len(shape)==4:
      x = tf.transpose(x,[0,3,1,2])
    print('last bn shape:', x.shape)
  return x

# BN for 3DCNN
def BatchNorm3d(x,center=True, scale=True, is_training=True, decay=0.9, epsilon=1./(2**15), Random=True, data_format='NDHWC'):
  with tf.variable_scope('BatchNorm',reuse=tf.AUTO_REUSE):
    shape = x.get_shape().as_list()
    #if data_format=='NCHW' and len(shape)==4:
    #  x = tf.transpose(x,[0,2,3,1]) # to NDHWC
    #  pritn('batch norma shape:', x.shape)
    reduce_axis = [0,1,2,3] if len(shape) == 5 else [0]

    channel = x.get_shape().as_list()[-1]
    if center:
        beta = tf.Variable(tf.constant(0.0,tf.float32,shape=[channel]),
        name='beta') 
    else:
        beta = None
    if scale:
        gamma = tf.Variable(tf.constant(1.0,tf.float32,shape=[channel]),
        name='gamma') 
    else:
        gamma = None


    moving_mean = tf.Variable(tf.constant(0.0,tf.float32,shape=[channel]),
      name='moving_mean', trainable=False)
    
    

    moving_variance = tf.Variable(tf.constant(1.0,tf.float32,shape=[channel]),
      name='moving_variance', trainable=False)
   
    if is_training:  
      
      mean, variance = tf.nn.moments(x, reduce_axis, name='moments')
      if Random is not None:
        mean = mean * tf.random_uniform([], minval=1.0-Random, maxval=1.0+Random)
        variance = variance * tf.random_uniform([], minval=1.0-Random, maxval=1.0+Random)
              
      update_mean = moving_averages.assign_moving_average(moving_mean, mean, decay, False)
      update_variance = moving_averages.assign_moving_average(moving_variance, variance, decay, False)
      ops.add_to_collections(ops.GraphKeys.UPDATE_OPS, update_mean)
      ops.add_to_collections(ops.GraphKeys.UPDATE_OPS, update_variance)

      x = batch_normalization(x, mean, variance, beta, gamma, epsilon)
    else:
      x = batch_normalization(x, moving_mean, moving_variance, beta , gamma , epsilon)

  return x
