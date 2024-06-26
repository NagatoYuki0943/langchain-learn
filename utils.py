import os
import re
import uuid
import random
from typing import Literal
from langchain_core.documents import Document
import hashlib


def is_used_rag(
    reject_answer: str,
    history: list,
) -> bool:
    """是否使用过rag"""
    if len(history) == 0:
        return False
    prompts, responses = zip(*history)
    # 去重回答
    responses = list(set(responses))
    # 经过去重之后只有一种回答,并且回答是拒绝回答说明没使用rag
    if len(responses) == 1 and responses[0] == reject_answer:
        return False
    else:
        return True


def get_filename(path: str):
    """
    './data\\FM docs 2024.3\\JOM_1998_13_4_06_The_Application_of_the_Hardin_Jones-Pauling-.pdf'
    ->
    ('./data\\FM docs 2024.3',
    'JOM_1998_13_4_06_The_Application_of_the_Hardin_Jones-Pauling-.pdf')
    """
    basepath, filename = os.path.split(path)
    return filename


def format_documents(documents: list[Document]) -> str:
    return "\n".join([doc.page_content for doc in documents])


def format_references(references: list[str]) -> str:
    if len(references) == 0:
        return "\n*no reference.*"
    else:
        references = [f"*{reference}*" for reference in references]
        references_str = "\n".join(references)
        return f"\nreferences: \n{references_str}"


def remove_history_references(history: list) -> list:
    split_words = ["\n*no reference.*", "\nreferences:"]
    split_words = [re.escape(word) for word in split_words]
    new_history = []
    for prompt, response in history:
        # 按照参考说明拆分,只保留拆分前的内容
        response_no_reference = re.split("|".join(split_words), response)[0]
        new_history.append([prompt, response_no_reference])
    return new_history


def download_openxlab_dataset(
    dataset_repo: str = 'NagatoYuki0943/FMdocs',
    target_path: str = './data/',
    access_key: str | None = None,
    secret_key: str | None = None
):
    import openxlab
    from openxlab.dataset import get

    print("start download dataset")
    openxlab.login(ak=access_key, sk=secret_key, relogin=True)
    get(dataset_repo=dataset_repo, target_path=target_path) # 数据集下载
    print("finish download dataset")


def random_uuid(dtype: Literal['int', 'str', 'bytes', 'time'] = 'int') -> int | str | bytes:
    """生成随机uuid
    reference: https://github.com/vllm-project/vllm/blob/main/vllm/utils.py
    """
    assert dtype in ['int', 'str', 'bytes', 'time'], f"unsupported dtype: {dtype}, should be in ['int', 'str', 'bytes', 'time']"

    # uuid4: 由伪随机数得到，有一定的重复概率，该概率可以计算出来。
    uid = uuid.uuid4()
    if dtype == 'int':
        return uid.int
    elif dtype == 'str':
        return uid.hex
    elif dtype == 'bytes':
        return uid.bytes
    else:
        return uid.time


def random_uuid_int() -> int:
    """random_uuid 生成的 int uuid 会超出int64的范围,lmdeploy使用会报错"""
    return random.getrandbits(64)


# write by codeium
def hashfile(file: str):
    sha256 = hashlib.sha256()
    with open(file, 'rb') as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()
