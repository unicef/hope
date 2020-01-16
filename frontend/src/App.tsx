import React from 'react';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch,
} from 'react-router-dom';
import { ApolloProvider } from '@apollo/react-hooks';
import { theme } from './theme';
import { HomeRouter } from './containers/HomeRouter';
import { LoginPage } from './containers/pages/LoginPage';
import { client } from './apollo/client';

export const App: React.FC = () => {
  const authenticated = true;
  return (
    <ApolloProvider client={client}>
      <ThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <Router>
            <Switch>
              <Route path='/login'>
                <LoginPage />
              </Route>
              <Route path='/'>
                {!authenticated ? <Redirect to='/login' /> : <HomeRouter />}
              </Route>
            </Switch>
          </Router>
        </StyledThemeProvider>
      </ThemeProvider>
    </ApolloProvider>
  );
};
