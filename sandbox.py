from clip_embeddings import embed_text, embed_image

feats = embed_text(["example text", "another one"])

feats.cpu().numpy()
