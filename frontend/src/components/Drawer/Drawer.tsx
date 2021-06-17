import clsx from 'clsx';
import IconButton from '@material-ui/core/IconButton';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import Divider from '@material-ui/core/Divider';
import List from '@material-ui/core/List';
import DrawerMaterial from '@material-ui/core/Drawer';
import React, { useEffect, useState } from 'react';
import { makeStyles } from '@material-ui/core';
import { gql } from 'apollo-boost';
import { useQuery } from '@apollo/react-hooks';
import { theme as themeObj } from '../../theme';
import { Logo } from '../Logo';
import packageJson from '../../../package.json';
import { AlertDialog } from '../AlertDialog';
import { DrawerItems } from './DrawerItems';

const useStyles = makeStyles((theme: typeof themeObj) => ({
  toolbarHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingLeft: '51px',
    backgroundColor: theme.hctPalette.lightBlue,
    color: 'white',
    borderRightWidth: 2,
    borderRightColor: '#02367D',
    borderRightStyle: 'solid',
    boxShadow:
      '0px 2px 4px 0px rgba(0,0,0,0.2), 0px 4px 5px 0px rgba(0,0,0,0.14), 0px 1px 10px 0px rgba(0,0,0,0.12)',
    ...theme.mixins.toolbar,
  },
  collapseIcon: {
    color: '#fff',
    opacity: 0.54,
  },
  drawerPaper: {
    position: 'relative',
    whiteSpace: 'nowrap',
    width: theme.drawer.width,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
    borderWidth: 0,
  },
  drawerPaperClose: {
    overflowX: 'hidden',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    width: theme.spacing(16),
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(14),
    },
  },
  list: {
    borderRightWidth: 2,
    borderRightColor: '#E1E1E1',
    borderRightStyle: 'solid',
    height: '100%',
  },
  version: {
    borderRightWidth: 2,
    borderRightColor: '#E1E1E1',
    color: '#aaa',
    borderRightStyle: 'solid',
    padding: 4,
    textAlign: 'center',
  },
}));
interface Props {
  open: boolean;
  handleDrawerClose: () => void;
  currentLocation: string;
  dataCy: string;
}

const GET_BACKEND_VERSION = gql`
  {
    backendVersion @client
  }
`;

export function Drawer({
  open,
  handleDrawerClose,
  currentLocation,
  dataCy,
}: Props): React.ReactElement {
  const classes = useStyles({});
  const [showMismatchedDialog, setShowMismatchedDialog] = useState(false);
  const { data } = useQuery(GET_BACKEND_VERSION, { fetchPolicy: 'cache-only' });
  const backendVersion = data?.backendVersion;
  const frontendVersion = packageJson.version;
  useEffect(() => {
    if (
      !showMismatchedDialog &&
      backendVersion &&
      frontendVersion &&
      backendVersion !== frontendVersion
    ) {
      setShowMismatchedDialog(true);
    }
  }, [backendVersion, frontendVersion, showMismatchedDialog]);
  return (
    <DrawerMaterial
      variant='permanent'
      classes={{
        paper: clsx(classes.drawerPaper, !open && classes.drawerPaperClose),
      }}
      open={open}
      data-cy={dataCy}
    >
      <div className={classes.toolbarHeader}>
        <Logo transparent={false} displayLogoWithoutSubtitle />
        <IconButton
          onClick={handleDrawerClose}
          className={classes.collapseIcon}
        >
          <ChevronLeftIcon />
        </IconButton>
      </div>
      <Divider />
      <List className={classes.list}>
        <DrawerItems currentLocation={currentLocation} />
      </List>
      <div className={classes.version}>
        <div>Backend Version: {backendVersion}</div>
        <div>Frontend Version: {frontendVersion}</div>
      </div>
      <AlertDialog
        show={showMismatchedDialog}
        message='Version mismatch, please refresh page'
      />
    </DrawerMaterial>
  );
}
