## model.py
import math
from typing import Optional, Callable

import torch
import torch.nn as nn
import torch.nn.functional as F


class PositionalEncoding(nn.Module):
    """
    Implements fixed sinusoidal positional encodings.
    For each position pos and dimension i, computes:
      PE(pos, 2i)   = sin(pos / (10000^(2i/d_model)))
      PE(pos, 2i+1) = cos(pos / (10000^(2i/d_model)))
    The positional encodings are added to the input embeddings.
    """

    def __init__(self, d_model: int, dropout: float, max_len: int = 5000) -> None:
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(dropout)
        # Create constant 'pe' matrix with values dependent on pos and i
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)  # Shape: (max_len, 1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float) * (-math.log(10000.0) / d_model)
        )  # Shape: (d_model/2)
        pe[:, 0::2] = torch.sin(position * div_term)  # Even indices
        pe[:, 1::2] = torch.cos(position * div_term)  # Odd indices
        pe = pe.unsqueeze(0)  # Shape: (1, max_len, d_model)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape (batch_size, seq_len, d_model)
        Returns:
            Tensor of shape (batch_size, seq_len, d_model) after adding positional encodings and applying dropout.
        """
        seq_len = x.size(1)
        x = x + self.pe[:, :seq_len]
        return self.dropout(x)


class MultiHeadAttention(nn.Module):
    """
    Implements Multi-Head Attention mechanism with scaled dot-product attention and optional masking.
    """

    def __init__(self, d_model: int, num_heads: int, dropout: float) -> None:
        super(MultiHeadAttention, self).__init__()
        if d_model % num_heads != 0:
            raise ValueError("d_model must be divisible by num_heads.")
        self.d_model: int = d_model
        self.num_heads: int = num_heads
        self.d_k: int = d_model // num_heads

        # Learned linear projections for queries, keys, and values.
        self.linear_q = nn.Linear(d_model, d_model)
        self.linear_k = nn.Linear(d_model, d_model)
        self.linear_v = nn.Linear(d_model, d_model)

        # Final output linear layer.
        self.linear_out = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Args:
            query: Tensor of shape (batch_size, seq_len_query, d_model)
            key: Tensor of shape (batch_size, seq_len_key, d_model)
            value: Tensor of shape (batch_size, seq_len_key, d_model)
            mask: (Optional) Boolean tensor of shape broadcastable to (batch_size, num_heads, seq_len_query, seq_len_key)
                  True values in the mask indicate positions that should be masked.
        Returns:
            Output tensor of shape (batch_size, seq_len_query, d_model)
        """
        batch_size = query.size(0)

        # Linear projections and splitting into heads
        q = self.linear_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        k = self.linear_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        v = self.linear_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        # Scaled dot-product attention scores: (batch_size, num_heads, seq_len_query, seq_len_key)
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.d_k)

        if mask is not None:
            scores = scores.masked_fill(mask, float("-inf"))

        attn = torch.softmax(scores, dim=-1)
        attn = self.dropout(attn)

        # Weighted sum over values.
        output = torch.matmul(attn, v)  # Shape: (batch_size, num_heads, seq_len_query, d_k)
        # Concatenate heads and reshape.
        output = output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        output = self.linear_out(output)
        return output


class FeedForward(nn.Module):
    """
    Implements the Position-wise Feed-Forward Network.
    Consists of two linear transformations with a ReLU activation in between.
    """

    def __init__(self, d_model: int, d_ff: int, dropout: float) -> None:
        super(FeedForward, self).__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear2(self.dropout(F.relu(self.linear1(x))))


class SublayerConnection(nn.Module):
    """
    Implements a residual connection followed by layer normalization.
    Output: LayerNorm(x + Dropout(sublayer(x)))
    """

    def __init__(self, d_model: int, dropout: float) -> None:
        super(SublayerConnection, self).__init__()
        self.norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, sublayer: Callable[[torch.Tensor], torch.Tensor]) -> torch.Tensor:
        return self.norm(x + self.dropout(sublayer(x)))


class EncoderLayer(nn.Module):
    """
    Encoder layer composed of a multi-head self-attention sub-layer and a position-wise feed-forward network,
    each wrapped with residual connection and layer normalization.
    """

    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float) -> None:
        super(EncoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        self.sublayer1 = SublayerConnection(d_model, dropout)
        self.sublayer2 = SublayerConnection(d_model, dropout)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        x = self.sublayer1(x, lambda _x: self.self_attn(_x, _x, _x, mask))
        x = self.sublayer2(x, self.feed_forward)
        return x


class Encoder(nn.Module):
    """
    Stacks multiple EncoderLayers and applies a final layer normalization.
    """

    def __init__(self, num_layers: int, d_model: int, num_heads: int, d_ff: int, dropout: float) -> None:
        super(Encoder, self).__init__()
        self.layers = nn.ModuleList(
            [EncoderLayer(d_model, num_heads, d_ff, dropout) for _ in range(num_layers)]
        )
        self.norm = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        for layer in self.layers:
            x = layer(x, mask)
        return self.norm(x)


class DecoderLayer(nn.Module):
    """
    Decoder layer composed of a masked multi-head self-attention sub-layer,
    an encoder-decoder multi-head attention sub-layer, and a position-wise feed-forward network,
    each with residual connections and layer normalization.
    """

    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float) -> None:
        super(DecoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.src_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        self.sublayer1 = SublayerConnection(d_model, dropout)
        self.sublayer2 = SublayerConnection(d_model, dropout)
        self.sublayer3 = SublayerConnection(d_model, dropout)

    def forward(
        self,
        x: torch.Tensor,
        memory: torch.Tensor,
        tgt_mask: Optional[torch.Tensor] = None,
        memory_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        x = self.sublayer1(x, lambda _x: self.self_attn(_x, _x, _x, tgt_mask))
        x = self.sublayer2(x, lambda _x: self.src_attn(_x, memory, memory, memory_mask))
        x = self.sublayer3(x, self.feed_forward)
        return x


class Decoder(nn.Module):
    """
    Stacks multiple DecoderLayers and applies a final layer normalization.
    """

    def __init__(self, num_layers: int, d_model: int, num_heads: int, d_ff: int, dropout: float) -> None:
        super(Decoder, self).__init__()
        self.layers = nn.ModuleList(
            [DecoderLayer(d_model, num_heads, d_ff, dropout) for _ in range(num_layers)]
        )
        self.norm = nn.LayerNorm(d_model)

    def forward(
        self,
        x: torch.Tensor,
        memory: torch.Tensor,
        tgt_mask: Optional[torch.Tensor] = None,
        memory_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        for layer in self.layers:
            x = layer(x, memory, tgt_mask, memory_mask)
        return self.norm(x)


class Model(nn.Module):
    """
    Transformer Model implementing the complete architecture from "Attention Is All You Need".
    Provides methods for forward pass, saving, and loading the model.
    Expects input data as a dictionary with keys 'src' and 'tgt'.
    """

    def __init__(self, params: dict) -> None:
        super(Model, self).__init__()
        # Extract model configuration parameters with default values.
        model_cfg = params.get("model", {})
        self.num_layers: int = model_cfg.get("num_layers", 6)
        self.d_model: int = model_cfg.get("d_model", 512)
        self.d_ff: int = model_cfg.get("d_ff", 2048)
        self.num_heads: int = model_cfg.get("num_heads", 8)
        self.dropout_rate: float = model_cfg.get("dropout", 0.1)
        self.label_smoothing: float = model_cfg.get("label_smoothing", 0.1)
        self.positional_encoding_type: str = model_cfg.get("positional_encoding", "sinusoidal")

        # Determine vocabulary size from data configuration; default to 37000.
        data_cfg = params.get("data", {})
        self.vocab_size: int = data_cfg.get("en_de_vocab_size", 37000)

        # Shared token embedding layer.
        self.embedding = nn.Embedding(self.vocab_size, self.d_model)

        # Positional Encoding: use sinusoidal by default.
        if self.positional_encoding_type == "sinusoidal":
            self.positional_encoding = PositionalEncoding(self.d_model, self.dropout_rate)
        else:
            # Fallback to dropout if not using sinusoidal (could implement learned embeddings if needed)
            self.positional_encoding = None
            self.dropout = nn.Dropout(self.dropout_rate)

        # Encoder and Decoder stacks.
        self.encoder = Encoder(self.num_layers, self.d_model, self.num_heads, self.d_ff, self.dropout_rate)
        self.decoder = Decoder(self.num_layers, self.d_model, self.num_heads, self.d_ff, self.dropout_rate)

        # Final linear output projection. Weight tied with embedding.
        self.output_layer = nn.Linear(self.d_model, self.vocab_size)
        self.output_layer.weight = self.embedding.weight

    def forward(self, x: dict, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Performs a forward pass of the Transformer model.

        Args:
            x: A dictionary with keys 'src' and 'tgt' corresponding to source and target token IDs.
               - 'src': Tensor of shape (batch_size, src_seq_len)
               - 'tgt': Tensor of shape (batch_size, tgt_seq_len)
            mask: An optional mask tensor (not used directly as masks are generated internally).

        Returns:
            Logits tensor of shape (batch_size, tgt_seq_len, vocab_size)
        """
        # Ensure that both source and target sequences are provided.
        src: Optional[torch.Tensor] = x.get("src", None)
        tgt: Optional[torch.Tensor] = x.get("tgt", None)
        if src is None or tgt is None:
            raise ValueError("Input dictionary must contain 'src' and 'tgt' keys.")

        # Default pad token ID set to 0.
        pad_id: int = 0

        # Create source mask for encoder: mask positions where token equals pad_id.
        # Shape: (batch_size, 1, 1, src_seq_len)
        src_mask = (src == pad_id).unsqueeze(1).unsqueeze(2)

        # Construct target mask combining pad mask and subsequent (look-ahead) mask.
        batch_size, tgt_len = tgt.size()
        # Subsequent mask: mask out future positions (upper-triangular part).
        subsequent_mask = torch.triu(
            torch.ones((tgt_len, tgt_len), device=tgt.device, dtype=torch.bool), diagonal=1
        )
        # Target pad mask: True where token equals pad_id.
        tgt_pad_mask = (tgt == pad_id).unsqueeze(1).unsqueeze(2)
        # Combine pad mask and subsequent mask (broadcast subsequent_mask to match dimensions).
        tgt_mask = tgt_pad_mask | subsequent_mask.unsqueeze(0).unsqueeze(0)

        # Embed source tokens and scale by sqrt(d_model).
        src_emb = self.embedding(src) * math.sqrt(self.d_model)
        if self.positional_encoding is not None:
            src_emb = self.positional_encoding(src_emb)
        else:
            src_emb = self.dropout(src_emb)

        # Encoder forward pass.
        memory = self.encoder(src_emb, src_mask)

        # Embed target tokens and scale.
        tgt_emb = self.embedding(tgt) * math.sqrt(self.d_model)
        if self.positional_encoding is not None:
            tgt_emb = self.positional_encoding(tgt_emb)
        else:
            tgt_emb = self.dropout(tgt_emb)

        # Decoder forward pass.
        output = self.decoder(tgt_emb, memory, tgt_mask, src_mask)

        # Apply final output linear layer to produce logits.
        logits = self.output_layer(output)
        return logits

    def save_model(self, path: str) -> None:
        """
        Saves the model parameters to the specified path.
        """
        torch.save(self.state_dict(), path)

    def load_model(self, path: str) -> None:
        """
        Loads model parameters from the specified path.
        """
        state_dict = torch.load(path, map_location=torch.device("cpu"))
        self.load_state_dict(state_dict)
