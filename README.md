# pgm-el

This is the source code for [1].

+ train.py/test.py are the main files for training and testing, respectively.
+ SampleRank.py records the core algorithm of SampleRank
+ Feature.py: returns the score calculated by each feature
+ Cangen.py/Alternative-cangen.py are two approaches of generating candidate entities and recording relevant values
+ canEntity.py, Entity.py, Mention.py are classes

The dataset can be obtained via the official approach.

Other data sources that have been utilized can be found via following repository links:
+ https://github.com/masha-p/PPRforNED
+ https://github.com/ag-sc/NERFGUN

[1] Weixin Zeng, Jiuyang Tang, Xiang Zhao, Bin Ge, Weidong Xiao: Named Entity Disambiguation via Probabilistic Graphical Model with Embedding Features. In Proceedings of 25th International Conference on Neural Information Processing (ICONIP), Siem Reap, Cambodia, December 13-16, 2018, Part III, 16-27.
