#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
import sys

import numpy as np
import tensorflow as tf

# create a Model class for Encoder
class Encoder(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, encoder_size, batch_size):
        super(Encoder, self).__init__()
        self.batch_size = batch_size
        self.encoder_size = encoder_size
        self.embedding = tf.keras.layers.Embedding(
            input_dim=vocab_size,
            output_dim=embedding_dim
        )
        self.biLSTM = tf.keras.layers.Bidirectional(
            tf.keras.layers.LSTM(
                units=self.encoder_size,
                return_sequences=True,
                return_state=True
            )
        )

    def call(self, inputs):
        inputs = self.embedding(inputs)
        output = self.biLSTM(inputs)
        # the output is a list consisting
        # concatenated encoder outputs(forward and backward), 
        # context and hidden for both forward and backward LSTMs
        return output[0]