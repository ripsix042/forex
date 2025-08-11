import os
import json
import datetime
from typing import Dict, List, Any, Optional

from src.config import PROCESSED_DIR

# Optional imports with fallbacks
try:
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib not available, chart generation will be disabled")

class LearningVisualizer:
    def __init__(self):
        self.processed_dir = PROCESSED_DIR
    
    def generate_learning_stats(self) -> Dict[str, Any]:
        """Generate statistics about the system's learning progress"""
        stats = {
            "total_files_processed": 0,
            "concepts_by_frequency": {},
            "patterns_by_frequency": {},
            "indicators_by_frequency": {},
            "learning_timeline": [],
            "content_types": {}
        }
        
        # Process all files in the processed directory
        if os.path.exists(self.processed_dir):
            processed_files = [f for f in os.listdir(self.processed_dir) if f.endswith(".json")]
            stats["total_files_processed"] = len(processed_files)
            
            for filename in processed_files:
                file_path = os.path.join(self.processed_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Extract metadata
                    metadata = data.get("metadata", {})
                    content_type = metadata.get("content_type", "unknown")
                    processed_date = metadata.get("processed_date", "")
                    
                    # Update content type stats
                    stats["content_types"][content_type] = stats["content_types"].get(content_type, 0) + 1
                    
                    # Update timeline
                    if processed_date:
                        stats["learning_timeline"].append({
                            "date": processed_date,
                            "file": metadata.get("filename", "unknown"),
                            "type": content_type
                        })
                    
                    # Extract knowledge
                    extracted = data.get("extracted_knowledge", {})
                    
                    # Update concept frequencies
                    for concept in extracted.get("concepts", []):
                        stats["concepts_by_frequency"][concept] = stats["concepts_by_frequency"].get(concept, 0) + 1
                    
                    # Update pattern frequencies
                    for pattern in extracted.get("patterns", []):
                        stats["patterns_by_frequency"][pattern] = stats["patterns_by_frequency"].get(pattern, 0) + 1
                    
                    # Update indicator frequencies
                    for indicator in extracted.get("indicators", []):
                        stats["indicators_by_frequency"][indicator] = stats["indicators_by_frequency"].get(indicator, 0) + 1
                    
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
            
            # Sort dictionaries by frequency
            stats["concepts_by_frequency"] = dict(sorted(
                stats["concepts_by_frequency"].items(), 
                key=lambda item: item[1], 
                reverse=True
            ))
            
            stats["patterns_by_frequency"] = dict(sorted(
                stats["patterns_by_frequency"].items(), 
                key=lambda item: item[1], 
                reverse=True
            ))
            
            stats["indicators_by_frequency"] = dict(sorted(
                stats["indicators_by_frequency"].items(), 
                key=lambda item: item[1], 
                reverse=True
            ))
            
            # Sort timeline by date
            stats["learning_timeline"] = sorted(
                stats["learning_timeline"],
                key=lambda x: x["date"] if x["date"] else "0"
            )
        
        return stats
    
    def generate_concept_chart(self, output_path: str = None) -> str:
        """Generate a bar chart of the most common trading concepts"""
        if not MATPLOTLIB_AVAILABLE:
            return "Chart generation not available: matplotlib is not installed"
            
        stats = self.generate_learning_stats()
        concepts = stats["concepts_by_frequency"]
        
        # Take top 10 concepts
        top_concepts = dict(list(concepts.items())[:10])
        
        if not top_concepts:
            return "No concepts found"
        
        try:
            # Create the chart
            plt.figure(figsize=(10, 6))
            plt.bar(top_concepts.keys(), top_concepts.values())
            plt.xlabel('Trading Concepts')
            plt.ylabel('Frequency')
            plt.title('Top Trading Concepts Learned')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Save the chart if output path is provided
            if output_path:
                plt.savefig(output_path)
                return output_path
            else:
                # Generate a temporary file path
                temp_path = os.path.join(self.processed_dir, f"concept_chart_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png")
                plt.savefig(temp_path)
                plt.close()
                return temp_path
        except Exception as e:
            print(f"Error generating concept chart: {e}")
            return f"Error generating chart: {e}"
    
    def generate_learning_timeline_chart(self, output_path: str = None) -> str:
        """Generate a timeline chart of learning progress"""
        if not MATPLOTLIB_AVAILABLE:
            return "Chart generation not available: matplotlib is not installed"
            
        stats = self.generate_learning_stats()
        timeline = stats["learning_timeline"]
        
        if not timeline:
            return "No timeline data found"
        
        try:
            # Group by date
            dates = {}
            for entry in timeline:
                date = entry["date"].split("T")[0] if "T" in entry["date"] else entry["date"]
                dates[date] = dates.get(date, 0) + 1
            
            # Sort dates
            sorted_dates = sorted(dates.items())
            
            # Create the chart
            plt.figure(figsize=(10, 6))
            plt.plot([d[0] for d in sorted_dates], [d[1] for d in sorted_dates], marker='o')
            plt.xlabel('Date')
            plt.ylabel('Files Processed')
            plt.title('Learning Timeline')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Save the chart if output path is provided
            if output_path:
                plt.savefig(output_path)
                return output_path
            else:
                # Generate a temporary file path
                temp_path = os.path.join(self.processed_dir, f"timeline_chart_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png")
                plt.savefig(temp_path)
                plt.close()
                return temp_path
        except Exception as e:
            print(f"Error generating timeline chart: {e}")
            return f"Error generating chart: {e}"

# Create a singleton instance
learning_visualizer = LearningVisualizer()