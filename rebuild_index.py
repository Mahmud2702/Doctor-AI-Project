# ═══════════════════════════════════════════════════════════════════════════
# rebuild_index.py
# Run this after editing/adding files in knowledge/ to re-embed them:
#     python rebuild_index.py
# ═══════════════════════════════════════════════════════════════════════════

from dotenv import load_dotenv
load_dotenv()

from vectorstore import rebuild_index

if __name__ == "__main__":
    print("Rebuilding clinic knowledge vector index...")
    vs = rebuild_index()
    count = vs._collection.count()
    print(f"Done. {count} chunks indexed.")
