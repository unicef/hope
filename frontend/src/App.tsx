import React from 'react';
import { RelayEnvironmentProvider } from 'relay-hooks';
import { environment } from './relay/enviroment';
import { ThemeProvider } from '@material-ui/core';
import { Route, Switch, BrowserRouter as Router } from 'react-router-dom';
import { theme } from './theme';
import { Home } from './containers/Home';

export const App: React.FC = () => {
  return (
    <RelayEnvironmentProvider environment={environment}>
      <ThemeProvider theme={theme}>
        <Router>
          <Switch>
            <Route path='/'>
              <Home />
            </Route>
          </Switch>
        </Router>
      </ThemeProvider>
    </RelayEnvironmentProvider>
  );
};
