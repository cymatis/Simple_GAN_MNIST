# title: Simple GAN with two layer neural network
# author: Kuntal Ganguly
# date: 25/05/2017

'''
version info.
old version of python and packages were used to avoid compatibility issues

python==2.7
tensorflow==1.4.0
numpy==1.12.1
matplotlib==2.0.1
'''

import tensorflow as tf 
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.gridspec as gridspec
import os 
from tensorflow.examples.tutorials.mnist import input_data





def xavier_init(size): ## xavier initiation, this weight initialization method depends on quantity of nodes in each layer
    input_dim = size[0]
    xavier_variance = 1. / tf.sqrt(input_dim/2.)
    return tf.random_normal(shape=size, stddev=xavier_variance)

def plot(samples): ## draw plot of sample images and save plot as an image, if there is no './sample' folder, this will make new one.
    fig = plt.figure(figsize=(4, 4))
    gs = gridspec.GridSpec(4, 4)
    gs.update(wspace=0.05, hspace=0.05)

    for i, sample in enumerate(samples):
        ax = plt.subplot(gs[i])
        plt.axis('off')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect('equal')
        plt.imshow(sample.reshape(28, 28), cmap='Greys_r')

        ## if there is no './sample' folder, this will make new one. Otherwise, do nothing.
        if not(os.path.isdir('./sample')):
            os.makedirs(os.path.join('./sample'))

        ## this line will decide where the sample images will be saved, 'dpi' determine quality of images to be stored
        plt.savefig('./sample/sample' + str(num) + '.png', dpi=300) 

    return fig





# Random noise setting for Generator
Z = tf.placeholder(tf.float32, shape=[None, 100], name='Z')

#Generator parameter settings
G_W1 = tf.Variable(xavier_init([100, 128]), name='G_W1')
G_b1 = tf.Variable(tf.zeros(shape=[128]), name='G_b1')
G_W2 = tf.Variable(xavier_init([128, 784]), name='G_W2')
G_b2 = tf.Variable(tf.zeros(shape=[784]), name='G_b2')
theta_G = [G_W1, G_W2, G_b1, G_b2]

#Input Image MNIST setting for Discriminator [28x28=784]
X = tf.placeholder(tf.float32, shape=[None, 784], name='X')

#Discriminator parameter settings
D_W1 = tf.Variable(xavier_init([784, 128]), name='D_W1')
D_b1 = tf.Variable(tf.zeros(shape=[128]), name='D_b1')
D_W2 = tf.Variable(xavier_init([128, 1]), name='D_W2')
D_b2 = tf.Variable(tf.zeros(shape=[1]), name='D_b2')

theta_D = [D_W1, D_W2, D_b1, D_b2]

# Generator Network
def generator(z):
    G_h1 = tf.nn.relu(tf.matmul(z, G_W1) + G_b1)
    G_log_prob = tf.matmul(G_h1, G_W2) + G_b2
    G_prob = tf.nn.sigmoid(G_log_prob)

    return G_prob

# Discriminator Network
def discriminator(x):
    D_h1 = tf.nn.relu(tf.matmul(x, D_W1) + D_b1)
    D_logit = tf.matmul(D_h1, D_W2) + D_b2
    D_prob = tf.nn.sigmoid(D_logit)

    return D_prob, D_logit



G_sample = generator(Z)

D_real, D_logit_real = discriminator(X)
D_fake, D_logit_fake = discriminator(G_sample)

# Loss functions from the paper
D_loss = -tf.reduce_mean(tf.log(D_real) + tf.log(1. - D_fake))
G_loss = -tf.reduce_mean(tf.log(D_fake))


# Update D(X)'s parameters
D_solver = tf.train.AdamOptimizer().minimize(D_loss, var_list=theta_D)

# Update G(Z)'s parameters
G_solver = tf.train.AdamOptimizer().minimize(G_loss, var_list=theta_G)

def sample_Z(m, n):
    return np.random.uniform(-1., 1., size=[m, n])

batch_size = 128
Z_dim = 100

sess = tf.Session()
sess.run(tf.global_variables_initializer())

mnist = input_data.read_data_sets('MNIST/', one_hot=True)

i = 0 ## unused variable??
num = 0 ## counter for sample image renaming

for itr in range(1000000): ## max iteration is 1,000,000
    if itr % 1000 == 0: ## every 1000 iteration~
        samples = sess.run(G_sample, feed_dict={Z: sample_Z(16, Z_dim)}) ## generate sample by collecting 16 images
        num = num + 1000 ## iteration count
        plot(samples) ## make plot of 'sample' and save it as a image at './sample' directory

    X_mb, _ = mnist.train.next_batch(batch_size)

    _, D_loss_curr = sess.run([D_solver, D_loss], feed_dict={X: X_mb, Z: sample_Z(batch_size, Z_dim)}) ## get current loss from Discriminator
    _, G_loss_curr = sess.run([G_solver, G_loss], feed_dict={Z: sample_Z(batch_size, Z_dim)}) ## get current loss from Generator

    ## print current D and G loss at terminal, also this result can be saved as *.csv file by using '> *.csv' command at terminal level
    print('{:.4},'.format(D_loss_curr),'{:.4}'.format(G_loss_curr)) 

