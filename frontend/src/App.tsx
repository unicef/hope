import React, { useRef, useState } from 'react';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import IdleTimer from 'react-idle-timer';
import CssBaseline from '@material-ui/core/CssBaseline';
import { MuiPickersUtilsProvider } from '@material-ui/pickers';
import moment from 'moment';
import MomentUtils from '@date-io/moment';
import { ApolloProvider } from '@apollo/react-hooks';
import { theme } from './theme';
import { HomeRouter } from './containers/HomeRouter';
import { ProfilePage } from './containers/pages/ProfilePage';
import { client } from './apollo/client';
import { LoginPage } from './containers/pages/LoginPage';
import { DefaultRoute } from './containers/DefaultRoute';
import { SanctionList } from './containers/pages/SanctionList';
import { ProtectedRoute } from './components/ProtectedRoute';

export const App: React.FC = () => {
  let countdownInterval;
  let timeout;
  const fifteenMinutes = 1000 * 60 * 15;
  //eslint-disable-next-line
  const [timeoutCountdown, setTimeoutCountdown] = useState(0);
  const idleTimer = useRef(null);
  const clearSessionTimeout = (): void => {
    clearTimeout(timeout);
  };
  const clearSessionInterval = (): void => {
    clearInterval(countdownInterval);
  };
  const handleLogout = (): void => {
    clearSessionInterval();
    clearSessionTimeout();
    window.location.assign('/api/logout');
    localStorage.removeItem('AUTHENTICATED');
  };
  const onActive = (): void => {
    clearSessionInterval();
    clearSessionTimeout();
  };
  const onIdle = (): void => {
    const delay = 1000 * 1;
    if (localStorage.getItem('AUTHENTICATED') !== null) {
      timeout = setTimeout(() => {
        let countDown = 10;
        setTimeoutCountdown(countDown);
        countdownInterval = setInterval(() => {
          if (countDown > 0) {
            //eslint-disable-next-line
            setTimeoutCountdown(--countDown);
          } else {
            handleLogout();
          }
        }, 1000);
      }, delay);
    }
  };
  return (
    <ApolloProvider client={client}>
      <ThemeProvider theme={theme}>
        <StyledThemeProvider theme={theme}>
          <MuiPickersUtilsProvider libInstance={moment} utils={MomentUtils}>
            <CssBaseline />
            <IdleTimer
              ref={idleTimer}
              onActive={onActive}
              onIdle={onIdle}
              debounce={250}
              timeout={fifteenMinutes}
            />
            <Router>
              <Switch>
                <Route path='/login'>
                  <LoginPage />
                </Route>
                <ProtectedRoute
                  path='/sanction-list'
                  component={SanctionList}
                  location={window.location}
                />
                <Route path='/accounts/profile/'>
                  <ProfilePage />
                </Route>
                <Route path='/:businessArea/'>
                  <HomeRouter />
                </Route>
                <Route path='/'>
                  <DefaultRoute />
                </Route>
              </Switch>
            </Router>
          </MuiPickersUtilsProvider>
        </StyledThemeProvider>
      </ThemeProvider>
    </ApolloProvider>
  );
};
