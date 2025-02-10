import React, { useState, useEffect } from 'react';
import { Brain } from 'lucide-react';

interface WorkbenchLayoutProps {
  prompt: string;
}

const WorkbenchLayout = ({ prompt } : WorkbenchLayoutProps) => {
  const [thoughts, setThoughts] = useState<string[]>([]);
  const [currentThought, setCurrentThought] = useState(0);

  
  useEffect(() => {
    const orchestratorThoughts = [
      "Analyzing prompt for required document types and analysis tasks...",
      "Delegating PDF analysis to Document Agent...",
      "Initiating web search via Research Agent...",
      "Processing data tables with Analysis Agent...",
      "Generating summary with Writing Agent..."
    ];

    const interval = setInterval(() => {
      if (currentThought < orchestratorThoughts.length) {
        setThoughts(prev => [...prev, orchestratorThoughts[currentThought]]);
        setCurrentThought(prev => prev + 1);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [currentThought]);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Top Bar with Prompt and Orchestrator */}
      <div className="bg-white border-b shadow-sm p-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-sm text-gray-500 mb-2">Initial Prompt</div>
          <div className="text-lg font-medium mb-4">{prompt}</div>
          
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Brain className="w-4 h-4" />
            <span>Orchestrator Thoughts:</span>
          </div>
          <div className="mt-2 space-y-1">
            {thoughts.map((thought, index) => (
              <div 
                key={index} 
                className="text-sm text-gray-600 animate-fade-in"
              >
                • {thought}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Grid Layout */}
      <div className="p-6">
        <div className="grid grid-cols-6 grid-rows-6 gap-4 h-[calc(100vh-12rem)]">
          {/* Previous grid items... */}
          <div className="col-span-2 row-span-4 bg-white rounded-lg shadow-md p-4">
            <div className="text-sm text-gray-500 mb-2">PDF Document</div>
            <div className="w-full h-[90%] bg-gray-200 rounded animate-pulse"></div>
          </div>

          <div className="col-span-2 row-span-2 bg-white rounded-lg shadow-md p-4">
            <div className="text-sm text-gray-500 mb-2">Web Results</div>
            <div className="space-y-2">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-4 bg-gray-200 rounded animate-pulse"></div>
              ))}
            </div>
          </div>

          <div className="col-span-2 row-span-2 bg-white rounded-lg shadow-md p-4">
            <div className="text-sm text-gray-500 mb-2">Data Table</div>
            <div className="grid grid-cols-3 gap-2">
              {[...Array(9)].map((_, i) => (
                <div key={i} className="h-6 bg-gray-200 rounded animate-pulse"></div>
              ))}
            </div>
          </div>

          <div className="col-span-4 row-span-2 bg-white rounded-lg shadow-md p-4">
            <div className="text-sm text-gray-500 mb-2">Presentation Slides</div>
            <div className="flex gap-4 h-[80%]">
              {[1, 2, 3].map(i => (
                <div key={i} className="flex-1 bg-gray-200 rounded animate-pulse"></div>
              ))}
            </div>
          </div>

          <div className="col-span-2 row-span-2 bg-white rounded-lg shadow-md p-4">
            <div className="text-sm text-gray-500 mb-2">Code</div>
            <div className="space-y-1">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-3 bg-gray-200 rounded animate-pulse w-[85%]"></div>
              ))}
            </div>
          </div>

          <div className="col-span-2 row-span-2 bg-white rounded-lg shadow-md p-4">
            <div className="text-sm text-gray-500 mb-2">Summary</div>
            <div className="space-y-2">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-4 bg-gray-200 rounded animate-pulse"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkbenchLayout;