# coding:utf-8
from PIL import Image

from random import choice

import os
import numpy as np
import tensorflow as tf

number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z']
# 图像大小
IMAGE_HEIGHT = 27
IMAGE_WIDTH = 72
MAX_CAPTCHA = 4

local = os.getcwd()
filename = os.path.join(local,"code_deal") #请换成自己的文件储存文件的地址

# 验证码最长4字符; 固定为4


# 把彩色图像转为灰度图像（色彩对识别验证码没有什么用）
def convert2gray(img):
    if len(img.shape) > 2:
        gray = np.mean(img, -1)
        # 上面的转法较快，正规转法如下
        # r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]
        # gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray
    else:
        return img

"""
cnn在图像大小是2的倍数时性能最高, 如果你用的图像大小不是2的倍数，可以在图像边缘补无用像素。
np.pad(image,((2,3),(2,2)), 'constant', constant_values=(255,))  # 在图像上补2行，下补3行，左补2行，右补2行
"""
# 文本转向量
char_set = number + alphabet + ['_']  # 如果验证码长度小于4, '_'用来补齐
CHAR_SET_LEN = len(char_set)

def text2vec(text):
    text_len = len(text)
    if text_len > MAX_CAPTCHA:
        raise ValueError('验证码最长4个字符')

    vector = np.zeros(MAX_CAPTCHA * CHAR_SET_LEN)  # 4*37

    def char2pos(c):
        if c == '_':
            k = 36
            return k
        k = ord(c) - 48     #数字
        if k > 9:
            k = ord(c) - 55 - 32
        return k

    for i, c in enumerate(text):
        idx = i * CHAR_SET_LEN + char2pos(c)
        vector[idx] = 1
    return vector

# 向量转回文本
def vec2text(vec):
    char_pos = vec.nonzero()[0]     # 返回vec数组第一个不为0的下标
    text = []
    for i, c in enumerate(char_pos):
        char_idx = c % CHAR_SET_LEN
        if char_idx < 10:
            char_code = char_idx + ord('0')
        elif char_idx < 36:
            char_code = char_idx - 10 + ord('a')
        else:
            raise ValueError('error')
        text.append(chr(char_code))
    return "".join(text)


# 获取xx目录下的所有验证码文本，例如：happ.png
def gen_list(filename):
    captcha_list = []
    for root, dirnames, images_name in os.walk(filename):
        for image_name in images_name:
            captcha_list.append(image_name)
    captcha_list.remove('Thumbs.db')

    return captcha_list


# 获取验证码文本和验证码二维数组
def gen_captcha_text_and_image(filename):
    image_text = choice(gen_list(filename))                         #图片验证码文本
    image = np.array(Image.open(filename + "/" + image_text))      #图片验证码
    return image_text[:4], image


# 生成一个训练batch（一个训练样本）
# 每个batch获取batch_size次文本和图片
# 文本转为向量，图片转为一位数组
# 返回这一个batch的文本向量和图片数组
def get_next_batch(batch_size, filename):
    batch_x = np.zeros([batch_size, IMAGE_HEIGHT * IMAGE_WIDTH])  # Height * Wight
    batch_y = np.zeros([batch_size, MAX_CAPTCHA * CHAR_SET_LEN])  # 4 * 36

    for i in range(batch_size):
        text, image = gen_captcha_text_and_image(filename)
        image = convert2gray(image)  # 灰度化

        # 将图片数组一维化 同时将文本也对应在两个二维组的同一行
        batch_x[i, :] = image.flatten() / 255
        batch_y[i, :] = text2vec(text)
    # 返回该训练批次
    return batch_x, batch_y

####################################################################
# 申请占位符 按照图片
X = tf.placeholder(tf.float32, [None, IMAGE_HEIGHT * IMAGE_WIDTH])
Y = tf.placeholder(tf.float32, [None, MAX_CAPTCHA * CHAR_SET_LEN])
keep_prob = tf.placeholder(tf.float32)  # dropout

# 定义CNN
def crack_captcha_cnn(w_alpha=0.01, b_alpha=0.1):
    # 将占位符 转换为 按照图片给的新样式
    x = tf.reshape(X, shape=[-1, IMAGE_HEIGHT, IMAGE_WIDTH, 1])  # [占位, H, W, 灰度为1]

    # 3 conv layer
    w_c1 = tf.Variable(w_alpha * tf.random_normal([3, 3, 1, 32]))  # 从正太分布输出随机值      卷积窗口3*3
    b_c1 = tf.Variable(b_alpha * tf.random_normal([32]))
    conv1 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(x, w_c1, strides=[1, 1, 1, 1], padding='SAME'), b_c1))  # 卷积过程   H, W上滑动的步长  让卷积的输入和输入保持同样的尺寸
    conv1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')  # 因为希望整体上缩小图片尺寸，因此池化层的strides也设为横竖两个方向上以2为步长。
    conv1 = tf.nn.dropout(conv1, keep_prob)

    w_c2 = tf.Variable(w_alpha * tf.random_normal([3, 3, 32, 64]))
    b_c2 = tf.Variable(b_alpha * tf.random_normal([64]))
    conv2 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv1, w_c2, strides=[1, 1, 1, 1], padding='SAME'), b_c2))
    conv2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv2 = tf.nn.dropout(conv2, keep_prob)

    w_c3 = tf.Variable(w_alpha * tf.random_normal([3, 3, 64, 64]))
    b_c3 = tf.Variable(b_alpha * tf.random_normal([64]))
    conv3 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv2, w_c3, strides=[1, 1, 1, 1], padding='SAME'), b_c3))
    conv3 = tf.nn.max_pool(conv3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv3 = tf.nn.dropout(conv3, keep_prob)

    # Fully connected layer 全连接层
    w_d = tf.Variable(w_alpha * tf.random_normal([9 * 4 * 64, 1024]))       # 隐含节点
    b_d = tf.Variable(b_alpha * tf.random_normal([1024]))
    dense = tf.reshape(conv3, [-1, w_d.get_shape().as_list()[0]])
    dense = tf.nn.relu(tf.add(tf.matmul(dense, w_d), b_d))
    dense = tf.nn.dropout(dense, keep_prob)

    w_out = tf.Variable(w_alpha * tf.random_normal([1024, MAX_CAPTCHA * CHAR_SET_LEN]))
    b_out = tf.Variable(b_alpha * tf.random_normal([MAX_CAPTCHA * CHAR_SET_LEN]))
    out = tf.add(tf.matmul(dense, w_out), b_out)
    return out

# 训练
def train_crack_captcha_cnn():
    output = crack_captcha_cnn()
    with tf.name_scope('loss'):
        loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=output, labels=Y))  # 传入差异值和真实值
        tf.summary.scalar('loss', loss)
    optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)     # 优化loss
    predict = tf.reshape(output, [-1, MAX_CAPTCHA, CHAR_SET_LEN])
    max_idx_p = tf.argmax(predict, 2)                                           # 预测值
    max_idx_l = tf.argmax(tf.reshape(Y, [-1, MAX_CAPTCHA, CHAR_SET_LEN]), 2)    # 真实值
    correct_pred = tf.equal(max_idx_p, max_idx_l)   # 对比预测值和真实值
    with tf.name_scope('accuracy'):
        accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))    # 求每个batch的平均正确率
        tf.summary.scalar('accuracy', accuracy)
    saver = tf.train.Saver()
    with tf.Session() as sess:
        writer = tf.summary.FileWriter("logs/", sess.graph)
        merged = tf.summary.merge_all() #将所有Summary合并到一起

        # 从这到def train_crack_captcha_cnn():全为定义变量
        sess.run(tf.global_variables_initializer()) # 初始化以上定义的变量
        step = 0
        while True:
            batch_x, batch_y = get_next_batch(64,filename)
            _, loss_, summery = sess.run( [optimizer, loss, merged], feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.75})
            writer.add_summary(summery, step)
            print(step, loss_)

            # 每100 step计算一次准确率
            if step % 100 == 0:
                batch_x_test, batch_y_test = get_next_batch(100, filename)
                acc = sess.run(accuracy, feed_dict={X: batch_x_test, Y: batch_y_test, keep_prob: 1.})
                print(step, acc)
                if acc > 0.98:
                    saver.save(sess, ".model/crack_capcha.model", global_step=step)
                    break
            step += 1

if __name__ == '__main__':
    train_crack_captcha_cnn()