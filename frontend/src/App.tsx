import React from "react";
import { RelayEnvironmentProvider } from "relay-hooks";
import { LocationsContainer } from "./containers/LocationsContainer";
import { environment } from "./relay/enviroment";

export const App: React.FC = () => {
  return (
    <RelayEnvironmentProvider environment={environment}>
      <LocationsContainer />
    </RelayEnvironmentProvider>
  );
};
