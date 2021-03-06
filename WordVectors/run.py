# import libraries
import os
import pickle
import numpy as np
import tensorflow as tf

# import pre-processing utilities
from utils.preprocess import *
from model import SkipGram

print("Load corpus from pickle file...")
with open('nltk_reuters_corpus.pkl', 'rb') as f:
    corpus = pickle.load(f)

print("Building model...")
vocab_size, vocab = get_count_distinct(corpus)
word2idx, idx2word = get_vocab_dicts(vocab_size, vocab)
window_size = 2

# declare a Tensorflow graph
graph = tf.Graph()
with graph.as_default() as g:
    # create an instance of SkipGram model
    model = SkipGram(vocab_size=vocab_size, embedding_dim=128,
                     window_size=window_size, batch_size=16, graph=g)

    # configure GPU options
    sess_config = tf.ConfigProto(allow_soft_placement=True)
    sess_config.gpu_options.allow_growth = True

    # start the Tensorflow session
    with tf.Session(config=sess_config) as sess:

        # writer and saver objects
        writer = tf.summary.FileWriter("./logs")
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        # check for already present checkpoint files
        if os.path.exists(os.path.join("./save_dir", "checkpoint")):
            saver.restore(sess, tf.train.latest_checkpoint("./save_dir"))
            # write embeddings to a numpy array for using them
            print("Writing Embeddings to a file...")
            np.save("./embeddings.npy", model.embeddings.eval())
        global_step = max(sess.run(model.global_step), 1)

        # start training loop
        for _ in range(global_step, 150000):

            global_step = sess.run(model.global_step) + 1
            # batch for single training step
            context_indices, center_indices = generate_batch(
                corpus, word2idx, window_size=window_size, batch_size=model.batch_size)
            loss, train_op = sess.run([model.loss, model.train_op], feed_dict={
                model.context_indices: context_indices, model.center_idx: center_indices})
            # write loss(summary) for Tensorboard visualizations
            loss_sum = tf.Summary(value=[tf.Summary.Value(
                tag="model/loss", simple_value=loss), ])
            writer.add_summary(loss_sum, global_step)
            # print loss for every 1000 steps
            if global_step % 1000 == 0:
                print("Loss at step {} - {}".format(_, loss))
            # save model checkpoints for every 50000 steps
            if global_step % 50000 == 0:
                print("Saving checkpoint..")
                filename = os.path.join(
                    "./save_dir", "model_{}".format(global_step))
                saver.save(sess, filename)
