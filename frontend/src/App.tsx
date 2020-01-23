import React from 'react';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { ApolloProvider } from '@apollo/react-hooks';
import { theme } from './theme';
import { HomeRouter } from './containers/HomeRouter';
import { ProfilePage } from './containers/pages/ProfilePage';
import { client } from './apollo/client';
import { LoginPage } from './containers/pages/LoginPage';
import CssBaseline from '@material-ui/core/CssBaseline';

export const App: React.FC = () => {
  return (
    <ApolloProvider client={client}>
      <ThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <CssBaseline />
          <Router>
            <Switch>
              <Route path='/login'>
                <LoginPage />
              </Route>
              <Route path='/accounts/profile/'>
                <ProfilePage />
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
