import clsx from 'clsx';
import IconButton from '@material-ui/core/IconButton';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import Divider from '@material-ui/core/Divider';
import List from '@material-ui/core/List';
import DrawerMaterial from '@material-ui/core/Drawer';
import React from 'react';
import { makeStyles } from '@material-ui/core';
import { theme as themeObj } from '../../theme';
import { DrawerItems } from './DrawerItems';

const useStyles = makeStyles((theme: typeof themeObj) => ({
  toolbarHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 0 0 31px',
    backgroundColor: theme.palette.primary.main,
    color: 'white',
    boxShadow:
      '0px 2px 4px -1px rgba(0,0,0,0.2), 0px 4px 5px 0px rgba(0,0,0,0.14), 0px 1px 10px 0px rgba(0,0,0,0.12)',
    ...theme.mixins.toolbar,
  },
  collapseIcon: {
    color: '#fff',
    opacity: 0.54,
  },
  hctMisLogo: {
    ...theme.hctTypography.font,
    fontSize: '16px',
    fontWeight: 500,
    lineHeight: '19px',
  },
  drawerPaper: {
    position: 'relative',
    whiteSpace: 'nowrap',
    width: theme.drawer.width,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  drawerPaperClose: {
    overflowX: 'hidden',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    width: theme.spacing(7),
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(9),
    },
  },
}));
interface Props {
  open: boolean;
  handleDrawerClose: () => void;
  currentLocation: string;
}

export function Drawer({
  open,
  handleDrawerClose,
  currentLocation,
}: Props): React.ReactElement {
  const classes = useStyles({});
  return (
    <DrawerMaterial
      variant='permanent'
      classes={{
        paper: clsx(classes.drawerPaper, !open && classes.drawerPaperClose),
      }}
      open={open}
    >
      <div className={classes.toolbarHeader}>
        <div className={classes.hctMisLogo}>
          <div>HCT-MIS</div>
          <div>PORTAL</div>
        </div>
        <IconButton
          onClick={handleDrawerClose}
          className={classes.collapseIcon}
        >
          <ChevronLeftIcon />
        </IconButton>
      </div>
      <Divider />
      <List>
        <DrawerItems currentLocation={currentLocation} />
      </List>
    </DrawerMaterial>
  );
}
