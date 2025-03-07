JOB_NAME = "7b_pretrain"
DO_ALERT = False

SAVE_CKPT_FOLDER = "local:ckpts/7b_pretrain"  # checkpoint 的保存路径
CHECKPOINT_EVERY = 1000  # 每过多少步保存一次 checkpoint
VALID_EVERY = 1000  # 每过多少步验证一次
TRAIN_FOLDER = "data/train"  # 训练数据的路径
VALID_FOLDER = "data/val"  # 验证数据的路径
ENABLE_TENSORBOARD = True  # 是否启用 TensorBoard
LOG_DIR = "logs"  # TensorBoard 日志文件夹

# 以下配置项定义了模型的结构（参数量）
SEQ_LEN = 1024
HIDDEN_SIZE = 2048
NUM_ATTENTION_HEAD = 32
MLP_RATIO = 8 / 3
NUM_LAYER = 32
VOCAB_SIZE = 103168

# 以下是其他更详细的配置

ckpt = dict(
    enable_save_ckpt=True,  # enable ckpt save.
    save_ckpt_folder=SAVE_CKPT_FOLDER,  # Path to save training ckpt.
    load_optimizer=True,  # Wheter to load optimizer states when continuing training.
    checkpoint_every=CHECKPOINT_EVERY,
    snapshot_ckpt_folder="/".join(
        [SAVE_CKPT_FOLDER, "snapshot"]
    ),  # directory for snapshot ckpt storage path.
)

data = dict(
    seq_len=SEQ_LEN,
    # micro_num means the number of micro_batch contained in one gradient update
    micro_num=4,
    # packed_length = micro_bsz * SEQ_LEN
    micro_bsz=1,
    # defaults to the value of micro_num
    valid_micro_num=4,
    # defaults to 0, means disable evaluate
    valid_every=VALID_EVERY,
    pack_sample_into_one=False,
    total_steps=50000,
    skip_batches="",
    rampup_batch_size="",
    # Datasets with less than 50 rows will be discarded
    min_length=50,
    train_folder=TRAIN_FOLDER,
    valid_folder=VALID_FOLDER,
)

grad_scaler = dict(
    fp16=dict(
        # the initial loss scale, defaults to 2**16
        initial_scale=2**16,
        # the minimum loss scale, defaults to None
        min_scale=1,
        # the number of steps to increase loss scale when no overflow occurs
        growth_interval=1000,
    ),
    # the multiplication factor for increasing loss scale, defaults to 2
    growth_factor=2,
    # the multiplication factor for decreasing loss scale, defaults to 0.5
    backoff_factor=0.5,
    # the maximum loss scale, defaults to None
    max_scale=2**24,
    # the number of overflows before decreasing loss scale, defaults to 2
    hysteresis=2,
)

hybrid_zero_optimizer = dict(
    # Enable low_level_optimzer overlap_communication
    overlap_sync_grad=True,
    overlap_sync_param=True,
    # bucket size for nccl communication params
    reduce_bucket_size=512 * 1024 * 1024,
    # grad clipping
    clip_grad_norm=1.0,
)

loss = dict(
    label_smoothing=0,
)

adam = dict(
    lr=1e-4,
    adam_beta1=0.9,
    adam_beta2=0.95,
    adam_beta2_c=0,
    adam_eps=1e-8,
    weight_decay=0.01,
)

lr_scheduler = dict(
    total_steps=data["total_steps"],
    init_steps=0,  # optimizer_warmup_step
    warmup_ratio=0.01,
    eta_min=1e-5,
    last_epoch=-1,
)

beta2_scheduler = dict(
    init_beta2=adam["adam_beta2"],
    c=adam["adam_beta2_c"],
    cur_iter=-1,
)

model = dict(
    checkpoint=False,  # The proportion of layers for activation aheckpointing, the optional value are True/False/[0-1]
    num_attention_heads=NUM_ATTENTION_HEAD,
    embed_split_hidden=True,
    vocab_size=VOCAB_SIZE,
    embed_grad_scale=1,
    parallel_output=True,
    hidden_size=HIDDEN_SIZE,
    num_layers=NUM_LAYER,
    mlp_ratio=MLP_RATIO,
    apply_post_layer_norm=False,
    dtype="torch.float16",  # Support: "torch.float16", "torch.half", "torch.bfloat16", "torch.float32", "torch.tf32"
    norm_type="rmsnorm",
    layer_norm_epsilon=1e-5,
    use_flash_attn=True,
    num_chunks=1,  # if num_chunks > 1, interleaved pipeline scheduler is used.
)
"""
zero1 parallel:
    1. if zero1 <= 0, The size of the zero process group is equal to the size of the dp process group,
        so parameters will be divided within the range of dp.
    2. if zero1 == 1, zero is not used, and all dp groups retain the full amount of model parameters.
    3. zero1 > 1 and zero1 <= dp world size, the world size of zero is a subset of dp world size.
        For smaller models, it is usually a better choice to split the parameters within nodes with a setting <= 8.
pipeline parallel (dict):
    1. size: int, the size of pipeline parallel.
    2. interleaved_overlap: bool, enable/disable communication overlap when using interleaved pipeline scheduler.
tensor parallel: tensor parallel size, usually the number of GPUs per node.
"""
# parallel = dict(
#     zero1=1,
#     pipeline=dict(size=1, interleaved_overlap=True),
#     sequence_parallel=False,
# )
parallel = dict(
    zero1=dict(size=1),
    # tensor=dict(size=1, mode="mtp"),
    pipeline=dict(size=1, interleaved_overlap=True),
    # weight=dict(size=1, overlap=True),
    sequence_parallel=False,
)


cudnn_deterministic = False
cudnn_benchmark = False

enable_tb = ENABLE_TENSORBOARD
tensorboard_folder = LOG_DIR
