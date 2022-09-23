import React from 'react';
import { useParams } from 'react-router-dom';

export function CommunicationDetailsPage(): React.ReactElement {
  const { id } = useParams();
  console.log(id, "varun")

  return (
    <>
      hai
    </>
  );
}
