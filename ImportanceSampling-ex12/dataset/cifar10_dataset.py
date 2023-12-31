import os
import torchvision as tv
import numpy as np
from PIL import Image


def get_dataset_CL(args, transform_train):
    cifar_train = Cifar10Train(args, train=True, transform=transform_train, download = args.download)
    return cifar_train



def get_dataset(args, transform_train, transform_test):
    if args.validation_exp == "True":
        temp_dataset = Cifar10Train(args, train=True, transform=transform_train, download = args.download)
        train_indexes, val_indexes = train_val_split(args, temp_dataset.train_labels)
        cifar_train = Cifar10Train(args, train=True, transform=transform_train, sample_indexes = train_indexes)
        testset = Cifar10Train(args, train=True, transform=transform_test, sample_indexes = val_indexes)
    else:
        cifar_train = Cifar10Train(args, train=True, transform=transform_train, download = args.download)
        testset = tv.datasets.CIFAR10(root='./data', train=False, download=False, transform=transform_test)

    return cifar_train, testset

def train_val_split(args, train_val):
    np.random.seed(args.seed_dataset)
    train_val = np.array(train_val)
    train_indexes = []
    val_indexes = []
    val_num = int(args.val_samples / args.num_classes)

    for id in range(args.num_classes):
        indexes = np.where(train_val == id)[0]
        np.random.shuffle(indexes)
        val_indexes.extend(indexes[:val_num])
        train_indexes.extend(indexes[val_num:])
    np.random.shuffle(train_indexes)
    np.random.shuffle(val_indexes)

    return train_indexes, val_indexes

class Cifar10Train(tv.datasets.CIFAR10):
    def __init__(self, args, train=True, transform=None, target_transform=None, sample_indexes = None, download=False):
        super(Cifar10Train, self).__init__(args.train_root, train=train, transform=transform, target_transform=target_transform, download=download)
        self.root = os.path.expanduser(args.train_root)
        self.transform = transform
        self.target_transform = target_transform
        self.args = args
        if sample_indexes is not None:
            self.train_data = self.train_data[sample_indexes]
            self.train_labels = np.array(self.train_labels)[sample_indexes]
        self.num_classes = self.args.num_classes

        self.data = self.train_data
        self.labels = np.asarray(self.train_labels, dtype=np.long)

        self.train_samples_idx = []
        self.train_probs = np.ones(len(self.labels))*(-1)
        self.avg_probs = np.ones(len(self.labels))*(-1)
        self.times_seen = np.ones(len(self.labels))*1e-6


    def __getitem__(self, index):
        img, labels = self.data[index], self.labels[index]
        img = Image.fromarray(img)

        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            labels = self.target_transform(labels)

        return img, labels, index