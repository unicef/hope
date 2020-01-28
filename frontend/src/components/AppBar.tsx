import React, { useState } from 'react';
import clsx from 'clsx';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import MenuIcon from '@material-ui/icons/Menu';
import MuiAppBar from '@material-ui/core/AppBar';
import { makeStyles, MenuItem, Select } from '@material-ui/core';
import { MiśTheme } from '../theme';
import { useAllLocationsQuery } from '../__generated__/graphql';
import { getCurrentLocation } from '../utils/utils';

const useStyles = makeStyles((theme: MiśTheme) => ({
  root: {
    display: 'flex',
  },
  toolbar: {
    paddingRight: 24,
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

const CountrySelect = styled(Select)`
  && {
    width: ${({ theme }) => theme.spacing(58)}px;
    background-color: rgba(104, 119, 127, 0.5);
    color: #e3e6e7;
    border-bottom-width: 0;
    border-radius: 4px;
    height: 40px;
  }
  .MuiFilledInput-input {
    padding: 0 10px;
    background-color: transparent;
  }
  .MuiSelect-select:focus {
    background-color: transparent;
  }
  .MuiSelect-icon {
    color: #e3e6e7;
  }
  &&:hover {
    border-bottom-width: 0;
    border-radius: 4px;
  }
  &&:hover::before {
    border-bottom-width: 0;
  }
  &&::before {
    border-bottom-width: 0;
  }
  &&::after {
    border-bottom-width: 0;
  }
  &&::after:hover {
    border-bottom-width: 0;
  }
`;

export function CountryCombo() {
  const { data } = useAllLocationsQuery({ fetchPolicy: 'cache-and-network' });
  const [value, setValue] = useState(getCurrentLocation());
  const history = useHistory();
  const onChange = (e): void => {
    localStorage.setItem('LocationId', e.target.value);
    setValue(e.target.value);
    history.push('/');
  };
  if (!data) {
    return null;
  }
  return (
    <CountrySelect variant='filled' value={value} onChange={onChange}>
      {data.allLocations.edges.map((each) => (
        <MenuItem key={each.node.id} value={each.node.id}>
          {each.node.country}
        </MenuItem>
      ))}
    </CountrySelect>
  );
}

export function AppBar({ open, handleDrawerOpen }): React.ReactElement {
  const classes = useStyles({});
  return (
    <MuiAppBar
      position='absolute'
      className={clsx(classes.appBar, open && classes.appBarShift)}
    >
      <Toolbar className={classes.toolbar}>
        <IconButton
          edge='start'
          color='inherit'
          aria-label='open drawer'
          onClick={handleDrawerOpen}
          className={clsx(classes.menuButton, open && classes.menuButtonHidden)}
        >
          <MenuIcon />
        </IconButton>
        <CountryCombo />
      </Toolbar>
    </MuiAppBar>
  );
}
