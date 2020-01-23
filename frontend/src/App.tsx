import React, { useEffect } from 'react';
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
import { LOGIN_URL } from './config';
import { getCookie, isAuthenticated } from './utils/utils';




export const App: React.FC = () => {
  return (
    <ApolloProvider client={client}>
      <ThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <Router>
            <Switch>
              <Route path='/accounts/profile/'>
                <LoginPage />
              </Route>
              <Route path='/'>
                  <HomeRouter />
              </Route>
            </Switch>
          </Router>
        </StyledThemeProvider>
      </ThemeProvider>
    </ApolloProvider>
  );
};
