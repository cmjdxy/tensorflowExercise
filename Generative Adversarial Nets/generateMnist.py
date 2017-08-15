#coding:utf-8
import tensorflow as tf
import numpy as np
from tensorflow.examples.tutorials.mnist import input_data
import argparse
import sys
FLAGS = None

def Generator(z):
    """
    Args:
        Z:random distribution,size:(100,)
    Return:
        G(z):Generate image
    """
    theta_G = []
    with tf.name_scope("G_nn1"):
        weight = tf.Variable(tf.truncated_normal(shape = [100,128],stddev=0.1),name = "G_weight",dtype="float32")
        bias = tf.Variable(tf.constant(0.1,shape=[128]),name = "G_bias")
        G_nn1_output = tf.nn.relu(tf.matmul(z,weight)+bias,name = "G_nn1_output")
        theta_G.append(weight)
        theta_G.append(bias)
    with tf.name_scope("G_nn2"):
        weight = tf.Variable(tf.truncated_normal(shape=[128,784],stddev=0.1),name = "G_weight",dtype="float32")
        bias = tf.Variable(tf.constant(0.1,shape=[784]),name = "G_bias")
        G_nn2_output = tf.nn.sigmoid(tf.matmul(G_nn1_output,weight)+bias,name="G_nn2_output")
        theta_G.append(weight)
        theta_G.append(bias)
    return G_nn2_output,theta_G

def Discriminator(x,reuse=None):
    """
    args:
        x:input image,size:(784,)
    return:
        prob and logits
    """
    theta_D = []
    with tf.variable_scope("D_nn1",reuse=reuse):
        weight = tf.get_variable(name="D_weight",initializer = tf.truncated_normal_initializer(stddev=0.1),shape=[784,128])
        bias = tf.get_variable(name = "D_bias",initializer = tf.constant_initializer(0.1),shape=[128])
        D_nn1_output = tf.nn.relu(tf.matmul(x,weight)+bias,name ="D_nn1_output")
        theta_D.append(weight)
        theta_D.append(bias)

    with tf.variable_scope("D_nn2",reuse=reuse):
        weight = tf.get_variable(name="D_weight",initializer = tf.truncated_normal_initializer(stddev=0.1),shape=[128,1])
        bias = tf.get_variable(name = "D_bias",initializer = tf.constant_initializer(0.1),shape=[1])
        D_nn2_prob = tf.matmul(D_nn1_output,weight)+bias
        D_nn2_output = tf.nn.sigmoid(D_nn2_prob,name = "D_nn2_output")
        theta_D.append(weight)
        theta_D.append(bias)
    return D_nn2_prob,D_nn2_output,theta_D

def sample(size):
    '''Uniform prior for G(Z)'''
    return np.random.uniform(-1., 1., size=size)

def training():
    #prepare mnist data
    data_set = input_data.read_data_sets(FLAGS.input_data_dir);

    z = tf.placeholder(tf.float32,[None,100],name = "Z")
    x = tf.placeholder(tf.float32,[None,784],name = "input")
    G_sample,theta_G= Generator(z)
    D_real,D_logit_real,theta_D= Discriminator(x)
    D_fake,D_logit_fake,_= Discriminator(G_sample,reuse=True)

    #loss function
    D_loss = -tf.reduce_mean(tf.log(D_real)+tf.log(1. -D_fake))
    G_loss = -tf.reduce_mean(tf.log(D_fake))


    #optimizer
    D_optimizer = tf.train.AdamOptimizer().minimize(D_loss, var_list=theta_D)
    G_optimizer = tf.train.AdamOptimizer().minimize(G_loss, var_list=theta_G)

    session = tf.Session()
    session.run(tf.global_variables_initializer())

    z_sample = sample([FLAGS.batch_size,100]);
    for step in range(FLAGS.max_steps):
        x_input,_ = data_set.train.next_batch(FLAGS.batch_size)

        _,D_loss_curr = session.run([D_optimizer,D_loss],feed_dict ={
            x:x_input,
            z:z_sample
            })
        _,G_loss_curr = session.run([G_optimizer,G_loss],feed_dict ={
            z:z_sample
            })
        if step%1000==0:
            print "step:{},D_loss:{},G_loss:{}".format(step,D_loss_curr,G_loss_curr)

def main(_):
    training()


if __name__=="__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--input_data_dir',
        type = str,
        default = "data/mnist",
        help = "directory of mnist data"
        )

    parser.add_argument(
        '--batch_size',
        type=int,
        default=256,
        help="batch size"
        )

    parser.add_argument(
        '--max_steps',
        type=int,
        default=10000,
        help='max steps'
        )

    FLAGS, unparsed = parser.parse_known_args()
    tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)