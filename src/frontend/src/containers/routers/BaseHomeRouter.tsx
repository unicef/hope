import CssBaseline from '@mui/material/CssBaseline';
import * as React from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAllBusinessAreasQuery } from '@generated/graphql';
import { AppBar } from '@components/core/AppBar';
import { Drawer } from '@components/core/Drawer/Drawer';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { styled as MuiStyled } from '@mui/system';
import { theme } from 'src/theme';

const Root = styled.div`
  display: flex;
  width: 100vw;
`;

const MainContent = styled.div`
  padding: 0px 1px;
  transition: margin-left 225ms cubic-bezier(0, 0, 0.2, 1) 0ms;
  width: 100%;
  flex-grow: 1;
  height: 100vh;
  overflow: auto;
`;

const AppBarSpacer = MuiStyled('div')(() => ({
  ...theme.mixins.toolbar,
}));

export const BaseHomeRouter: React.FC = () => {
  const [open, setOpen] = React.useState(true);
  const { businessArea } = useBaseUrl();
  const location = useLocation();
  const navigate = useNavigate();
  const handleDrawerOpen = (): void => {
    setOpen(true);
  };
  const handleDrawerClose = (): void => {
    setOpen(false);
  };
  const { data: businessAreaData, loading: businessAreaLoading } =
    useAllBusinessAreasQuery({
      variables: {
        slug: businessArea,
      },
      fetchPolicy: 'cache-first',
    });

  if (!businessAreaData || businessAreaLoading) {
    return <LoadingComponent />;
  }

  const allBusinessAreasSlugs = businessAreaData.allBusinessAreas.edges.map(
    (el) => el.node.slug,
  );
  const isBusinessAreaValid = allBusinessAreasSlugs.includes(businessArea);

  if (!isBusinessAreaValid) {
    navigate('/');
    return null;
  }

  return (
    <Root>
      <CssBaseline />
      <AppBar open={open} handleDrawerOpen={handleDrawerOpen} />
      <Drawer
        open={open}
        handleDrawerClose={handleDrawerClose}
        currentLocation={location.pathname}
        dataCy="side-nav"
      />
      <MainContent data-cy="main-content">
        <AppBarSpacer />
        <Outlet />
      </MainContent>
    </Root>
  );
};
