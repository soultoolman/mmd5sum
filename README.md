# mmd5sum: calculate multiple MD5s using multiple processing

If you have a huge many files that want to calculate MD5,
you will need `mmd5sum`. `mmd5sum` calculate a directory
of files (can have sub-directories) using multiple processes.


## installation

```shell
pip install mmd5sum
```

## features

1. can specify a directory (can have sub-directories)
2. can read calculated results to avoid recalculating
3. can specify how many processes to use
4. default using local machine command `md5sum`, but can specify another one

## usage

```shell
mmd5sum -d /path/to/directory -o md5.txt
```

If you have a file that some file already calculated:

```shell
mmd5sum -d /path/to/to/directory -i old_md5.txt -o new_md5.txt
```

If you want faster:

```shell
mmd5sum -d /path/to/directory -o md5.txt -p 10
```

`-p 10` means you will have 10 processes in parallel, default is 4.

`mmd5sum` default use `md5sum` command to calculate MD5,
if the command calculate MD5 on you machine isn't `md5sum`:

```shell
mmd5sum -d /path/to/directory -o md5.txt -m md5
```

`-m md5` means the command on your machine is `md5`。
