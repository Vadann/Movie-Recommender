import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Optional

MIN_RATINGS_FOR_NCF = 5
EMBEDDING_DIM = 32
EPOCHS = 20
BATCH_SIZE = 32

_MODEL_PATH = Path(__file__).parent / "ncf_model.keras"
_MAPPINGS_PATH = Path(__file__).parent / "ncf_mappings.json"


class NeuralCollaborativeFilter:
    def __init__(self, embedding_dim: int = EMBEDDING_DIM):
        self.embedding_dim = embedding_dim
        self.model = None
        self.user_to_idx: Dict[int, int] = {}
        self.movie_to_idx: Dict[int, int] = {}
        self.is_trained = False
        self._load_if_exists()

    def _build_model(self, num_users: int, num_movies: int):
        import tensorflow as tf
        from tensorflow.keras import layers

        user_input = tf.keras.Input(shape=(1,), name="user_id")
        movie_input = tf.keras.Input(shape=(1,), name="movie_id")

        user_vec = layers.Flatten()(
            layers.Embedding(num_users, self.embedding_dim, name="user_emb")(user_input)
        )
        movie_vec = layers.Flatten()(
            layers.Embedding(num_movies, self.embedding_dim, name="movie_emb")(movie_input)
        )

        x = layers.Concatenate()([user_vec, movie_vec])
        x = layers.Dense(64, activation="relu")(x)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(32, activation="relu")(x)
        output = layers.Dense(1, activation="sigmoid")(x)

        model = tf.keras.Model(inputs=[user_input, movie_input], outputs=output)
        model.compile(optimizer="adam", loss="mse", metrics=["mae"])
        return model

    def train(self, ratings_data: List[dict]) -> bool:
        if len(ratings_data) < MIN_RATINGS_FOR_NCF:
            print(f"[NCF] Need {MIN_RATINGS_FOR_NCF} ratings to train, have {len(ratings_data)}.")
            return False

        try:
            import tensorflow as tf
        except ImportError:
            print("[NCF] TensorFlow not installed.")
            return False

        user_ids = sorted(set(r["user_id"] for r in ratings_data))
        movie_ids = sorted(set(r["movie_id"] for r in ratings_data))

        self.user_to_idx = {uid: i for i, uid in enumerate(user_ids)}
        self.movie_to_idx = {mid: i for i, mid in enumerate(movie_ids)}

        user_arr = np.array([self.user_to_idx[r["user_id"]] for r in ratings_data])
        movie_arr = np.array([self.movie_to_idx[r["movie_id"]] for r in ratings_data])
        rating_arr = np.array([r["rating"] / 10.0 for r in ratings_data], dtype=np.float32)

        self.model = self._build_model(len(user_ids), len(movie_ids))
        self.model.fit(
            [user_arr, movie_arr],
            rating_arr,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            validation_split=0.1 if len(ratings_data) >= 10 else 0.0,
            verbose=0,
        )

        self.is_trained = True
        self._save()
        print(f"[NCF] Trained on {len(ratings_data)} ratings ({len(user_ids)} users, {len(movie_ids)} movies).")
        return True

    def predict_for_user(self, user_id: int, candidate_movie_ids: List[int]) -> Dict[int, float]:
        if not self.is_trained or self.model is None:
            return {}
        if user_id not in self.user_to_idx:
            return {}

        try:
            user_idx = self.user_to_idx[user_id]
            known = [(mid, self.movie_to_idx[mid]) for mid in candidate_movie_ids if mid in self.movie_to_idx]
            if not known:
                return {}

            movie_arr = np.array([m[1] for m in known])
            user_arr = np.full(len(movie_arr), user_idx)

            preds = self.model.predict([user_arr, movie_arr], verbose=0).flatten()
            return {m[0]: float(p) for m, p in zip(known, preds)}
        except Exception as e:
            print(f"[NCF] Prediction error: {e}")
            return {}

    def is_ready_for_user(self, user_id: int) -> bool:
        return self.is_trained and user_id in self.user_to_idx

    def _save(self):
        try:
            self.model.save(str(_MODEL_PATH))
            with open(_MAPPINGS_PATH, "w") as f:
                json.dump(
                    {
                        "user_to_idx": {str(k): v for k, v in self.user_to_idx.items()},
                        "movie_to_idx": {str(k): v for k, v in self.movie_to_idx.items()},
                    },
                    f,
                )
        except Exception as e:
            print(f"[NCF] Save failed: {e}")

    def _load_if_exists(self):
        try:
            if not (_MODEL_PATH.exists() and _MAPPINGS_PATH.exists()):
                return
            import tensorflow as tf

            self.model = tf.keras.models.load_model(str(_MODEL_PATH))
            with open(_MAPPINGS_PATH) as f:
                mappings = json.load(f)

            self.user_to_idx = {int(k): v for k, v in mappings["user_to_idx"].items()}
            self.movie_to_idx = {int(k): v for k, v in mappings["movie_to_idx"].items()}
            self.is_trained = True
            print(f"[NCF] Loaded model ({len(self.user_to_idx)} users, {len(self.movie_to_idx)} movies).")
        except Exception as e:
            print(f"[NCF] Could not load saved model: {e}")


_ncf_instance: Optional[NeuralCollaborativeFilter] = None


def get_ncf_model() -> NeuralCollaborativeFilter:
    global _ncf_instance
    if _ncf_instance is None:
        _ncf_instance = NeuralCollaborativeFilter()
    return _ncf_instance
