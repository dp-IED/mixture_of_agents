"use client";

import React, { useState, useEffect } from "react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { Brain } from "lucide-react";
import DraggableItem from "./DraggableItem";

interface WorkbenchLayoutProps {
  prompt: string;
}

interface GridItem {
  id: string;
  type: "pdf" | "web" | "data" | "slides" | "code" | "summary";
  content: string;
}

const WorkbenchLayout = ({ prompt }: WorkbenchLayoutProps) => {
  const [thoughts, setThoughts] = useState<string[]>([]);
  const [currentThought, setCurrentThought] = useState(0);
  const [gridItems, setGridItems] = useState<GridItem[]>([
    { id: "pdf", type: "pdf", content: "PDF Document" },
    { id: "web", type: "web", content: "Web Results" },
    { id: "data", type: "data", content: "Data Table" },
    { id: "slides", type: "slides", content: "Presentation Slides" },
    { id: "code", type: "code", content: "Code" },
    { id: "summary", type: "summary", content: "Summary" },
  ]);

  const moveItem = (dragIndex: number, hoverIndex: number) => {
    const updatedItems = [...gridItems];
    const [draggedItem] = updatedItems.splice(dragIndex, 1);
    updatedItems.splice(hoverIndex, 0, draggedItem);
    setGridItems(updatedItems);
  };

  useEffect(() => {
    const orchestratorThoughts = [
      "Analyzing prompt for required document types and analysis tasks...",
      "Delegating PDF analysis to Document Agent...",
      "Initiating web search via Research Agent...",
      "Processing data tables with Analysis Agent...",
      "Generating summary with Writing Agent...",
    ];

    const interval = setInterval(() => {
      if (currentThought < orchestratorThoughts.length) {
        setThoughts((prev) => [...prev, orchestratorThoughts[currentThought]]);
        setCurrentThought((prev) => prev + 1);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [currentThought]);

  // Optimized grid layout with exact fitting
  const getItemStyle = (type: string) => {
    switch (type) {
      case "pdf":
        return "bg-gray-200 col-span-4 row-span-3"; // Main document viewer
      case "web":
        return "bg-blue-200 col-span-4 row-span-2"; // Web results
      case "data":
        return "bg-yellow-200 col-span-2 row-span-2"; // Data visualization
      case "slides":
        return "bg-purple-200 col-span-2 row-span-1"; // Presentation preview
      case "code":
        return "bg-green-200 col-span-2 row-span-2"; // Code editor
      case "summary":
        return "bg-pink-200 col-span-2 row-span-1"; // Summary section
      default:
        return "bg-gray-200 col-span-2 row-span-1";
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="min-h-screen bg-gray-50">
        {/* Top Bar with Prompt and Orchestrator */}
        <div className="bg-white border-b shadow-sm p-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-sm font-medium text-gray-500 mb-2">Initial Prompt</div>
            <div className="text-lg font-medium mb-4">{prompt}</div>

            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Brain className="w-4 h-4" />
              <span>Orchestrator Thoughts:</span>
            </div>
            <div className="mt-2 space-y-1">
              {thoughts.map((thought, index) => (
                <div
                  key={index}
                  className="text-sm text-gray-600 animate-fade-in flex items-center gap-2"
                >
                  <div className="w-1 h-1 rounded-full bg-gray-400" />
                  {thought}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Perfect Grid Layout */}
        <div className="p-4">
          <div className="grid grid-cols-8 gap-4 h-[calc(100vh-12rem)]">
            {gridItems.map((item, index) => (
              <DraggableItem
                key={item.id}
                id={item.id}
                index={index}
                moveItem={moveItem}
                style={getItemStyle(item.type)}
              >
                <div className="h-full p-4 rounded-lg">
                  <div className="text-sm font-medium text-gray-700">
                    {item.content}
                  </div>
                </div>
              </DraggableItem>
            ))}
          </div>
        </div>
      </div>
    </DndProvider>
  );
};

export default WorkbenchLayout;