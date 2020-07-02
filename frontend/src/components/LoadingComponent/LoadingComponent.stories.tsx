import React from 'react';
import { LoadingComponent } from './LoadingComponent';

export default {
  component: LoadingComponent,
  title: 'Loading Component',
};

export const Loading = () => {
  return (
    <LoadingComponent isLoading={true} absolute />
  );
};
