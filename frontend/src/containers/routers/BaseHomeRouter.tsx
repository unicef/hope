import { makeStyles, Snackbar, SnackbarContent } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import React from 'react';
import { Redirect, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import {
  useAllBusinessAreasQuery,
  useAllProgramsForChoicesQuery,
} from '../../__generated__/graphql';
import { AppBar } from '../../components/core/AppBar';
import { Drawer } from '../../components/core/Drawer/Drawer';
import { LoadingComponent } from '../../components/core/LoadingComponent';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { useSnackbar } from '../../hooks/useSnackBar';
import { MiśTheme } from '../../theme';

const Root = styled.div`
  display: flex;
  max-width: 100%;
  overflow-x: hidden;
`;
const MainContent = styled.div`
  flex-grow: 1;
  overflow: auto;
  max-width: 100%;
  overflow-x: hidden;
`;

const useStyles = makeStyles((theme: MiśTheme) => ({
  appBarSpacer: theme.mixins.toolbar,
}));

export const BaseHomeRouter = ({ children }): React.ReactElement => {
  const [open, setOpen] = React.useState(true);
  const { businessArea, programId } = useBaseUrl();
  const classes = useStyles({});
  const location = useLocation();
  const snackBar = useSnackbar();
  const handleDrawerOpen = (): void => {
    setOpen(true);
  };
  const handleDrawerClose = (): void => {
    setOpen(false);
  };
  const {
    data: businessAreaData,
    loading: businessAreaLoading,
  } = useAllBusinessAreasQuery({
    variables: {
      slug: businessArea,
    },
    fetchPolicy: 'cache-first',
  });

  const {
    data: programsData,
    loading: programsLoading,
  } = useAllProgramsForChoicesQuery({
    variables: { businessArea, first: 100 },
    fetchPolicy: 'cache-first',
  });

  if (!businessAreaData) {
    return null;
  }

  if (businessAreaLoading) {
    return <LoadingComponent />;
  }

  if (!businessAreaData || !programsData) {
    return null;
  }

  if (businessAreaLoading || programsLoading) {
    return <LoadingComponent />;
  }
  const allBusinessAreasSlugs = businessAreaData.allBusinessAreas.edges.map(
    (el) => el.node.slug,
  );
  const isBusinessAreaValid = allBusinessAreasSlugs.includes(businessArea);

  if (!isBusinessAreaValid) {
    return <Redirect to='/' noThrow />;
  }

  return (
    <Root>
      <CssBaseline />
      <AppBar open={open} handleDrawerOpen={handleDrawerOpen} />
      <Drawer
        open={open}
        handleDrawerClose={handleDrawerClose}
        currentLocation={location.pathname}
        dataCy='side-nav'
      />
      <MainContent data-cy='main-content'>
        <div className={classes.appBarSpacer} />
        {children}
      </MainContent>
      {snackBar.show && (
        <Snackbar
          open={snackBar.show}
          autoHideDuration={5000}
          onClose={() => snackBar.setShow(false)}
        >
          <SnackbarContent
            message={snackBar.message}
            data-cy={snackBar.dataCy}
          />
        </Snackbar>
      )}
    </Root>
  );
};
