import React from 'react';
import {
  DragDropContext,
  Droppable,
  OnDragEndResponder,
} from 'react-beautiful-dnd';
import { PaymentInstructionDraggableListItem } from './PaymentInstructionDraggableListItem';

type Item = {
  id: string;
};

export type PaymentInstructionDraggableListProps = {
  items: Item[];
  onDragEnd: OnDragEndResponder;
  handleDeletePaymentInstruction: (id: string) => void;
};

export const PaymentInstructionDraggableList = React.memo(
  ({
    items,
    onDragEnd,
    handleDeletePaymentInstruction,
  }: PaymentInstructionDraggableListProps) => {
    return (
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId='droppable-list'>
          {(provided) => (
            <div ref={provided.innerRef} {...provided.droppableProps}>
              {items.map((item, index) => (
                <PaymentInstructionDraggableListItem
                  item={item}
                  index={index}
                  key={item.id}
                  handleDeletePaymentInstruction={
                    handleDeletePaymentInstruction
                  }
                />
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>
    );
  },
);
