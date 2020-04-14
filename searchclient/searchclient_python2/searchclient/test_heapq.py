#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 15:34:05 2020

@author: miki
"""

import heapq

q = []

x = (3, 'lalala')
y = (1, 'ladoado')
z = (2, 'ququququ')

heapq.heappush(q, y)
heapq.heappush(q, x)
heapq.heappush(q, z)

print(heapq)

print(heapq.heappop(q)[1])