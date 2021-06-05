import torch
import clip
from PIL import Image

from typing import Union, List
from clip.simple_tokenizer import SimpleTokenizer as _Tokenizer

_tokenizer = _Tokenizer()


def modified_tokenize(texts: Union[str, List[str]], context_length: int = 77) -> torch.LongTensor:
    """
    Returns the tokenized representation of given input string(s)
    Makes sure that the number of tokens doesn't exceed context length, rather than return an error.
    Parameters
    ----------
    texts : Union[str, List[str]]
        An input string or a list of input strings to tokenize
    context_length : int
        The context length to use; all CLIP models use 77 as the context length
    Returns
    -------
    A two-dimensional tensor containing the resulting tokens, shape = [number of input strings, context_length]
    """
    if isinstance(texts, str):
        texts = [texts]

    sot_token = _tokenizer.encoder["<|startoftext|>"]
    eot_token = _tokenizer.encoder["<|endoftext|>"]
    all_tokens = [[sot_token] + _tokenizer.encode(text) + [eot_token] for text in texts]
    result = torch.zeros(len(all_tokens), context_length, dtype=torch.long)

    for i, tokens in enumerate(all_tokens):
        if len(tokens) > context_length:
            # raise RuntimeError(f"Input {texts[i]} is too long for context length {context_length}")
            tokens = tokens[:context_length-1] + [eot_token]
        result[i, :len(tokens)] = torch.tensor(tokens)

    return result

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def embed_image(images):
    if type(images) == str: images = [images]
    with torch.no_grad():
        batch_size = 128
        imagest = preprocess(Image.open(images[0])).unsqueeze(0).to(device)
        image_features = model.encode_image(imagest)
        for i in range(1,len(images),batch_size):
            imagest = preprocess(Image.open(images[i])).unsqueeze(0).to(device)
            for image in images[i+1:i+batch_size]:
                imagest = torch.cat([imagest,preprocess(Image.open(image)).unsqueeze(0).to(device)],0)
            image_features = torch.cat([image_features,model.encode_image(imagest)],0)
        return image_features.cpu().numpy()

def embed_text(texts):
    if type(texts) == str: texts = [texts]
    with torch.no_grad():
        # text = clip.tokenize(texts).to(device)
        batch_size = 32
        text = modified_tokenize([texts[0]]).to(device)
        text_features = model.encode_text(text)
        for i in range(1,len(texts),batch_size):
            text = modified_tokenize(texts[i:i+batch_size]).to(device)
            text_features = torch.cat([text_features,model.encode_text(text)],0)
        return text_features.cpu().numpy()
