import hashlib
import mmh3
from simhash import Simhash
from subprober.logger.logger import Logger 
import argparse 

def tokenize_for_simhash(text: str) -> list[str]:
    return text.lower().split()

class HashGen:
    def __init__(self, algorithms: list[str], args: argparse.Namespace):
        self.algorithms = [alg.strip().lower() for alg in algorithms] 
        self.args = args
        self.logger = Logger() 

    async def gen(self, response: str) -> dict[str, str]:
        hashed_results = {}
        processed_response = ""

        try:
            processed_response = response.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Error processing response encoding for hashing: {e}, {type(e)}")
            return {} 
        for alg in self.algorithms:
            try:
                if alg == "md5":
                    hashed_results[alg] = hashlib.md5(processed_response.encode("utf-8")).hexdigest()
                elif alg == "sha1":
                    hashed_results[alg] = hashlib.sha1(processed_response.encode("utf-8")).hexdigest()
                elif alg == "sha256":
                    hashed_results[alg] = hashlib.sha256(processed_response.encode("utf-8")).hexdigest()
                elif alg == "sha512":
                    hashed_results[alg] = hashlib.sha512(processed_response.encode("utf-8")).hexdigest()
                elif alg == "mmh3":
                    hashed_results[alg] = str(mmh3.hash(processed_response.encode("utf-8")))
                elif alg == "simhash":
                    tokens = tokenize_for_simhash(processed_response)
                    if tokens:
                        hashed_results[alg] = str(Simhash(tokens).value)
                    else:
                        hashed_results[alg] = "" 
                        if self.args.verbose:
                            self.logger.warn(f"Simhash received empty tokens for response. Setting empty hash.")
                else:
                    if self.args.verbose:
                        self.logger.warn(f"Undefined or unsupported hash algorithm requested: '{alg}'")
            except Exception as inner_e:
                self.logger.warn(
                    f"Error generating hash for algorithm '{alg}': {inner_e}, {type(inner_e)}")
        
        return hashed_results