import React from 'react';
import clsx from 'clsx';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';
import MuiAppBar from '@material-ui/core/AppBar';
import styled from 'styled-components';
import { Avatar, Button, makeStyles, Menu, MenuItem } from '@material-ui/core';
import { MiśTheme } from '../theme';
import { BusinessAreaSelect } from '../containers/BusinessAreaSelect';
import { useMeQuery } from '../__generated__/graphql';
import {UserProfileMenu} from "../containers/UserProfileMenu";

const useStyles = makeStyles((theme: MiśTheme) => ({
  root: {
    display: 'flex',
  },
  toolbarIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 8px',
    ...theme.mixins.toolbar,
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    backgroundColor: theme.palette.secondary.main,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    marginLeft: theme.drawer.width,
    width: `calc(100% - ${theme.drawer.width}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  menuButton: {
    marginRight: 36,
  },
  menuButtonHidden: {
    display: 'none',
  },
  title: {
    flexGrow: 1,
  },
  appBarSpacer: theme.mixins.toolbar,
}));
const BusinessAreaContainer = styled.div`
  margin-left: ${({ theme }) => theme.spacing(11)}px;
`;
const StyledToolbar = styled(Toolbar)`
  display: flex;
  justify-content: space-between;
`;

export function AppBar({ open, handleDrawerOpen }): React.ReactElement {
  const { data: meData, loading: meLoading } = useMeQuery({
    fetchPolicy: 'cache-and-network',
  });
  const classes = useStyles({});
  if (meLoading) {
    return null;
  }
  return (
    <MuiAppBar
      position='absolute'
      className={clsx(classes.appBar, open && classes.appBarShift)}
    >
      <StyledToolbar>
        <IconButton
          edge='start'
          color='inherit'
          aria-label='open drawer'
          onClick={handleDrawerOpen}
          className={clsx(classes.menuButton, open && classes.menuButtonHidden)}
        >
          <MenuIcon />
        </IconButton>
        <BusinessAreaContainer>
          <BusinessAreaSelect />
        </BusinessAreaContainer>
        <UserProfileMenu meData={meData}/>
      </StyledToolbar>
    </MuiAppBar>
  );
}
