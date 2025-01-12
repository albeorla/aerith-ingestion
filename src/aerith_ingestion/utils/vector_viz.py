from typing import List, Optional, Tuple

import chromadb
import click
import numpy as np
import pandas as pd
import plotly.express as px
from umap import UMAP


def visualize_embeddings(
    embeddings: np.ndarray,
    labels: Optional[List[str]] = None,
    metadata: Optional[List[dict]] = None,
    title: str = "Vector Embeddings Visualization",
):
    """
    Visualize high-dimensional embeddings in 3D using UMAP and Plotly.

    Args:
        embeddings: numpy array of shape (n_samples, n_dimensions)
        labels: optional list of labels for each point
        metadata: optional list of metadata dicts for each point
        title: title for the plot
    """
    if len(embeddings) == 0:
        click.echo("No embeddings to visualize")
        return

    # Reduce dimensionality to 3D using UMAP
    umap = UMAP(n_components=3, random_state=42)
    embeddings_3d = umap.fit_transform(embeddings)

    # Create DataFrame for plotting
    plot_data = {
        "UMAP1": embeddings_3d[:, 0],
        "UMAP2": embeddings_3d[:, 1],
        "UMAP3": embeddings_3d[:, 2],
    }

    # Add metadata for hover information
    hover_data = []
    if metadata is not None:
        metadata_df = pd.DataFrame(metadata)

        # Extract task content from documents
        if "content" in metadata_df.columns:
            plot_data["Task"] = metadata_df["content"].apply(
                lambda x: x.split("\nDescription:")[0].replace("Task: ", "")
            )
            plot_data["Description"] = metadata_df["content"].apply(
                lambda x: (
                    x.split("\nDescription:")[1].strip()
                    if "\nDescription:" in x
                    else ""
                )
            )
            hover_data.extend(["Task", "Description"])

        # Add project_id for coloring
        if "project_id" in metadata_df.columns:
            plot_data["Project"] = metadata_df["project_id"]
            color_column = "Project"
            hover_data.append("Project")
        else:
            color_column = None

        # Add additional metadata if available
        if "priority" in metadata_df.columns:
            plot_data["Priority"] = metadata_df["priority"]
            hover_data.append("Priority")
        if "is_completed" in metadata_df.columns:
            plot_data["Completed"] = metadata_df["is_completed"]
            hover_data.append("Completed")
        if "due_date" in metadata_df.columns:
            plot_data["Due Date"] = metadata_df["due_date"]
            hover_data.append("Due Date")

    # Create interactive 3D scatter plot
    fig = px.scatter_3d(
        plot_data,
        x="UMAP1",
        y="UMAP2",
        z="UMAP3",
        color=color_column,
        title=title,
        hover_data=hover_data if hover_data else None,
        opacity=0.7,
    )

    # Update layout for better visualization
    fig.update_layout(
        scene=dict(xaxis_title="UMAP1", yaxis_title="UMAP2", zaxis_title="UMAP3"),
        width=1200,
        height=800,
        showlegend=True,
    )

    # Show the plot
    fig.show()


def get_collection_embeddings(
    collection,
) -> Tuple[np.ndarray, List[str], List[dict]]:
    """
    Extract embeddings from a ChromaDB or LangChain Chroma collection.

    Args:
        collection: ChromaDB collection or LangChain Chroma instance
    Returns:
        tuple of (embeddings array, list of ids, list of metadata dicts)
    """
    if hasattr(collection, "_collection"):  # LangChain Chroma
        collection = collection._collection

    # Get all items from collection with include_embeddings=True
    result = collection.get(include=["embeddings", "metadatas", "documents"])

    # Handle empty collection
    if not result or not result["embeddings"]:
        return np.array([]), [], []

    # Convert embeddings to numpy array
    embeddings = np.array(result["embeddings"])
    ids = result["ids"]
    metadatas = result["metadatas"]

    # Add document content to metadata for better visualization
    if "documents" in result and result["documents"]:
        for metadata, doc in zip(metadatas, result["documents"]):
            metadata["content"] = doc

    return embeddings, ids, metadatas


@click.group()
def cli():
    """Vector store visualization and management tools."""
    pass


@cli.command()
@click.option(
    "--persist-dir",
    "-p",
    required=True,
    type=click.Path(exists=True),
    help="ChromaDB persistence directory",
)
def list_collections(persist_dir: str):
    """List all available collections in the ChromaDB."""
    client = chromadb.PersistentClient(path=persist_dir)
    collections = client.list_collections()
    if not collections:
        click.echo("No collections found")
        return
    click.echo("\nAvailable collections:")
    for collection in collections:
        click.echo(f"- {collection.name} (count: {collection.count()})")


@cli.command()
@click.option(
    "--persist-dir",
    "-p",
    required=True,
    type=click.Path(exists=True),
    help="ChromaDB persistence directory",
)
@click.option(
    "--collection-name",
    "-c",
    required=True,
    help="Name of the collection to visualize",
)
@click.option(
    "--title",
    "-t",
    default="Vector Embeddings Visualization",
    help="Title for the visualization",
)
def visualize(persist_dir: str, collection_name: str, title: str):
    """Visualize embeddings from a ChromaDB collection."""
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=persist_dir)

    try:
        # Get collection
        collection = client.get_collection(collection_name)

        # Get embeddings and visualize
        embeddings, ids, metadatas = get_collection_embeddings(collection)

        if len(embeddings) == 0:
            click.echo(f"No embeddings found in collection '{collection_name}'")
            return

        click.echo(f"Visualizing {len(embeddings)} embeddings from '{collection_name}'")
        visualize_embeddings(embeddings, labels=ids, metadata=metadatas, title=title)

    except ValueError as e:
        click.echo(f"Error: {str(e)}")
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}")


@cli.command()
@click.option(
    "--persist-dir",
    "-p",
    required=True,
    type=click.Path(exists=True),
    help="ChromaDB persistence directory",
)
@click.option(
    "--collection-name",
    "-c",
    required=True,
    help="Name of the collection to inspect",
)
def debug(persist_dir: str, collection_name: str):
    """Debug collection contents."""
    client = chromadb.PersistentClient(path=persist_dir)
    try:
        collection = client.get_collection(collection_name)
        click.echo(f"\nCollection: {collection_name}")
        click.echo(f"Count: {collection.count()}")

        # Get raw data
        result = collection.get(include=["embeddings", "metadatas", "documents"])
        click.echo(f"\nEmbeddings: {len(result.get('embeddings', []))}")
        click.echo(
            f"Metadatas: {len(result['metadatas']) if 'metadatas' in result else 0}"
        )
        click.echo(
            f"Documents: {len(result['documents']) if 'documents' in result else 0}"
        )

        if result["metadatas"]:
            click.echo(f"\nSample metadata keys: {list(result['metadatas'][0].keys())}")

    except Exception as e:
        click.echo(f"Error: {str(e)}")


if __name__ == "__main__":
    cli()
