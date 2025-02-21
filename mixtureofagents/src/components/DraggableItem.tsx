"use client";

import React, { ReactNode } from "react";
import { useDrag, useDrop } from "react-dnd";

interface DraggableItemProps {
  id: string;
  index: number;
  style: string; // tailwind
  moveItem: (dragIndex: number, hoverIndex: number) => void;
  children: ReactNode;
}

const DraggableItem = ({ id, index, style, moveItem, children }: DraggableItemProps) => {
  // Hook for drop functionality
  const [, dropRef] = useDrop({
    accept: "CARD",
    hover: (item: { id: string; index: number }) => {
      const dragIndex = item.index;
      const hoverIndex = index;

      if (dragIndex !== hoverIndex) {
        moveItem(dragIndex, hoverIndex);
        item.index = hoverIndex; // Update the current index of the dragged item
      }
    },
  });

  // Hook for drag functionality
  const [{ isDragging }, dragRef] = useDrag({
    type: "CARD",
    item: { id, index },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  // Combine drag and drop refs
  const combinedRef = (el: HTMLElement | null) => {
    dragRef(el);
    dropRef(el);
  };

  const opacity = isDragging ? 0.5 : 1;

  return (
    <div
      ref={combinedRef} // Use the combined ref
      style={{ opacity }}
      className={style}
    >
      {children}
    </div>
  );
};

export default DraggableItem;
