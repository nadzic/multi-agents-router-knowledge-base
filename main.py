"""CLI-style demo entrypoint."""

from agent.agent import run_query_with_tracing


def main():
  """Run a quick demo query from terminal."""
  result = run_query_with_tracing("How do I authenticate API requests?")
  print("Original Query:", result["query"])
  print()
  print("Classifications:")
  for classification in result.get("classifications", []):
    print(f"  - {classification['source']}: {classification['query']}")
  print("\n" + "=" * 60 + "\n")
  print("Final answer:")
  print(result.get("final_answer", "No final answer generated."))


if __name__ == "__main__":
  main()
