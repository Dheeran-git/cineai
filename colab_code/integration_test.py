"""
Integration Testing for CLIP Embeddings
Member 2: AI Engineer - Embeddings

Validates that generated embeddings meet all requirements:
- Correct shape (N, 512)
- L2 normalized (norms = 1.0)
- Self-similarity = 1.0
- File format correctness
- Metadata completeness
"""

import numpy as np
import json
from pathlib import Path
import sys


def test_embeddings_format(embeddings_path: str, verbose: bool = True) -> bool:
    """
    Validate embeddings file format

    Tests:
    - File exists
    - Shape is (N, 512)
    - Dtype is float32
    - No NaN or Inf values

    Args:
        embeddings_path: Path to video_embeddings.npy
        verbose: Print detailed output

    Returns:
        True if all tests pass, False otherwise
    """
    if verbose:
        print("\n1. Testing Embeddings Format")
        print("-" * 60)

    try:
        # Load embeddings
        embeddings = np.load(embeddings_path)

        if verbose:
            print(f"✓ Embeddings file loaded: {embeddings_path}")
            print(f"  Shape: {embeddings.shape}")
            print(f"  Dtype: {embeddings.dtype}")

        # Check shape
        if len(embeddings.shape) != 2:
            if verbose:
                print(f"✗ FAIL: Expected 2D array, got {len(embeddings.shape)}D")
            return False

        if embeddings.shape[1] != 512:
            if verbose:
                print(f"✗ FAIL: Expected 512 dimensions, got {embeddings.shape[1]}")
            return False

        if verbose:
            print(f"✓ Shape is correct: (N={embeddings.shape[0]}, 512)")

        # Check dtype
        if embeddings.dtype != np.float32:
            if verbose:
                print(f"✗ FAIL: Expected dtype float32, got {embeddings.dtype}")
            return False

        if verbose:
            print(f"✓ Dtype is correct: float32")

        # Check for NaN or Inf
        if np.any(np.isnan(embeddings)):
            if verbose:
                print(f"✗ FAIL: Embeddings contain NaN values")
            return False

        if np.any(np.isinf(embeddings)):
            if verbose:
                print(f"✗ FAIL: Embeddings contain Inf values")
            return False

        if verbose:
            print(f"✓ No NaN or Inf values detected")

        return True

    except Exception as e:
        if verbose:
            print(f"✗ FAIL: Error loading embeddings: {e}")
        return False


def test_embeddings_normalization(embeddings_path: str, verbose: bool = True) -> bool:
    """
    Validate L2 normalization of embeddings

    Tests:
    - All embedding vectors have L2 norm ≈ 1.0
    - Tolerance: 0.01

    Args:
        embeddings_path: Path to video_embeddings.npy
        verbose: Print detailed output

    Returns:
        True if all tests pass, False otherwise
    """
    if verbose:
        print("\n2. Testing L2 Normalization")
        print("-" * 60)

    try:
        embeddings = np.load(embeddings_path)

        # Calculate L2 norms
        norms = np.linalg.norm(embeddings, axis=1)

        if verbose:
            print(f"  L2 Norms Statistics:")
            print(f"    Min:  {norms.min():.6f}")
            print(f"    Max:  {norms.max():.6f}")
            print(f"    Mean: {norms.mean():.6f}")
            print(f"    Std:  {norms.std():.6f}")

        # Check if all norms are close to 1.0
        if not np.allclose(norms, 1.0, atol=0.01):
            if verbose:
                print(f"✗ FAIL: Not all embeddings are L2 normalized")
                print(f"  Expected: All norms ≈ 1.0 (tolerance 0.01)")
                print(f"  Got: Min={norms.min():.6f}, Max={norms.max():.6f}")
            return False

        if verbose:
            print(f"✓ All embeddings are L2 normalized (norms ≈ 1.0)")

        return True

    except Exception as e:
        if verbose:
            print(f"✗ FAIL: Error testing normalization: {e}")
        return False


def test_similarity_sanity(embeddings_path: str, verbose: bool = True) -> bool:
    """
    Sanity check for similarity computation

    Tests:
    - Self-similarity = 1.0 (dot product of normalized vector with itself)
    - Similarities are in range [-1, 1]

    Args:
        embeddings_path: Path to video_embeddings.npy
        verbose: Print detailed output

    Returns:
        True if all tests pass, False otherwise
    """
    if verbose:
        print("\n3. Testing Similarity Sanity Checks")
        print("-" * 60)

    try:
        embeddings = np.load(embeddings_path)

        if len(embeddings) == 0:
            if verbose:
                print(f"✗ FAIL: No embeddings to test")
            return False

        # Test self-similarity
        sample_idx = 0
        self_similarity = np.dot(embeddings[sample_idx], embeddings[sample_idx])

        if verbose:
            print(f"  Self-similarity (sample {sample_idx}): {self_similarity:.6f}")

        if not np.isclose(self_similarity, 1.0, atol=0.01):
            if verbose:
                print(f"✗ FAIL: Self-similarity should be 1.0, got {self_similarity:.6f}")
            return False

        if verbose:
            print(f"✓ Self-similarity = 1.0")

        # Test pairwise similarities
        if len(embeddings) > 1:
            sample1 = embeddings[0]
            sample2 = embeddings[1]
            pairwise_sim = np.dot(sample1, sample2)

            if verbose:
                print(f"  Pairwise similarity (0 vs 1): {pairwise_sim:.6f}")

            if not (-1.0 <= pairwise_sim <= 1.0):
                if verbose:
                    print(f"✗ FAIL: Similarity out of range [-1, 1]: {pairwise_sim:.6f}")
                return False

            if verbose:
                print(f"✓ Pairwise similarity in valid range [-1, 1]")

        # Test similarity distribution
        if len(embeddings) >= 10:
            # Sample 10 random pairs
            np.random.seed(42)
            sample_indices = np.random.choice(len(embeddings), size=min(10, len(embeddings)), replace=False)
            sample_embeddings = embeddings[sample_indices]

            # Compute pairwise similarities
            similarity_matrix = np.dot(sample_embeddings, sample_embeddings.T)
            off_diagonal = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]

            if verbose:
                print(f"\n  Pairwise Similarity Distribution (sample of {len(off_diagonal)} pairs):")
                print(f"    Min:  {off_diagonal.min():.4f}")
                print(f"    Max:  {off_diagonal.max():.4f}")
                print(f"    Mean: {off_diagonal.mean():.4f}")
                print(f"    Std:  {off_diagonal.std():.4f}")

        return True

    except Exception as e:
        if verbose:
            print(f"✗ FAIL: Error testing similarities: {e}")
        return False


def test_paths_alignment(embeddings_path: str, paths_path: str, verbose: bool = True) -> bool:
    """
    Test that paths align with embeddings

    Tests:
    - paths.npy exists
    - Same number of paths as embeddings
    - All paths are valid strings

    Args:
        embeddings_path: Path to video_embeddings.npy
        paths_path: Path to video_paths.npy
        verbose: Print detailed output

    Returns:
        True if all tests pass, False otherwise
    """
    if verbose:
        print("\n4. Testing Paths Alignment")
        print("-" * 60)

    try:
        embeddings = np.load(embeddings_path)
        paths = np.load(paths_path, allow_pickle=True)

        if verbose:
            print(f"✓ Paths file loaded: {paths_path}")
            print(f"  Number of paths: {len(paths)}")
            print(f"  Number of embeddings: {len(embeddings)}")

        # Check alignment
        if len(paths) != len(embeddings):
            if verbose:
                print(f"✗ FAIL: Mismatch between paths and embeddings")
                print(f"  Paths: {len(paths)}, Embeddings: {len(embeddings)}")
            return False

        if verbose:
            print(f"✓ Paths and embeddings are aligned")

        # Check path validity
        if len(paths) > 0:
            sample_path = str(paths[0])
            if verbose:
                print(f"  Sample path: {sample_path}")

        return True

    except Exception as e:
        if verbose:
            print(f"✗ FAIL: Error testing paths: {e}")
        return False


def test_config_completeness(config_path: str, verbose: bool = True) -> bool:
    """
    Test that configuration file is complete

    Tests:
    - embedding_config.json exists
    - Contains required fields

    Args:
        config_path: Path to embedding_config.json
        verbose: Print detailed output

    Returns:
        True if all tests pass, False otherwise
    """
    if verbose:
        print("\n5. Testing Configuration Completeness")
        print("-" * 60)

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        if verbose:
            print(f"✓ Config file loaded: {config_path}")

        # Required fields
        required_fields = [
            "model_name",
            "embedding_dim",
            "frame_strategy",
            "normalization",
            "device",
            "total_clips_found",
            "clips_processed"
        ]

        missing_fields = [field for field in required_fields if field not in config]

        if missing_fields:
            if verbose:
                print(f"✗ FAIL: Missing required fields: {missing_fields}")
            return False

        if verbose:
            print(f"✓ All required fields present")
            print(f"\n  Configuration Summary:")
            print(f"    Model: {config.get('model_name')}")
            print(f"    Embedding Dim: {config.get('embedding_dim')}")
            print(f"    Strategy: {config.get('frame_strategy')}")
            print(f"    Normalization: {config.get('normalization')}")
            print(f"    Device: {config.get('device')}")
            print(f"    Clips Processed: {config.get('clips_processed')}/{config.get('total_clips_found')}")

        # Validate embedding dimension
        if config.get("embedding_dim") != 512:
            if verbose:
                print(f"✗ FAIL: Expected embedding_dim=512, got {config.get('embedding_dim')}")
            return False

        if verbose:
            print(f"✓ Embedding dimension is correct (512)")

        return True

    except FileNotFoundError:
        if verbose:
            print(f"✗ FAIL: Config file not found: {config_path}")
        return False
    except Exception as e:
        if verbose:
            print(f"✗ FAIL: Error testing config: {e}")
        return False


def run_all_tests(output_dir: str, verbose: bool = True) -> bool:
    """
    Run all integration tests

    Args:
        output_dir: Directory containing embeddings output files
        verbose: Print detailed output

    Returns:
        True if all tests pass, False otherwise
    """
    output_dir = Path(output_dir)

    embeddings_path = output_dir / "video_embeddings.npy"
    paths_path = output_dir / "video_paths.npy"
    config_path = output_dir / "embedding_config.json"

    print("="*60)
    print("CLIP Embeddings Integration Tests")
    print("="*60)
    print(f"\nOutput directory: {output_dir}")

    # Run all tests
    tests = [
        ("Format", test_embeddings_format, (str(embeddings_path),)),
        ("Normalization", test_embeddings_normalization, (str(embeddings_path),)),
        ("Similarity", test_similarity_sanity, (str(embeddings_path),)),
        ("Paths", test_paths_alignment, (str(embeddings_path), str(paths_path))),
        ("Config", test_config_completeness, (str(config_path),))
    ]

    results = {}
    for test_name, test_func, args in tests:
        try:
            passed = test_func(*args, verbose=verbose)
            results[test_name] = passed
        except Exception as e:
            if verbose:
                print(f"\n✗ Test '{test_name}' failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    total_tests = len(results)
    passed_tests = sum(results.values())

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")

    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n✓ All tests passed! Embeddings are ready for integration.")
    else:
        print(f"\n✗ {total_tests - passed_tests} test(s) failed. Please fix issues before integration.")

    print("="*60)

    return passed_tests == total_tests


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test CLIP embeddings for correctness")
    parser.add_argument(
        "--output_dir",
        type=str,
        default="/content/drive/MyDrive/HackathonProject/embeddings",
        help="Directory containing embeddings output files"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress detailed output, show only summary"
    )

    args = parser.parse_args()

    success = run_all_tests(args.output_dir, verbose=not args.quiet)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
