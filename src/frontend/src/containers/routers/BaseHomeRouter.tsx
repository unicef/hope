import CssBaseline from '@mui/material/CssBaseline';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { AppBar } from '@components/core/AppBar';
import { Drawer } from '@components/core/Drawer/Drawer';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { styled as MuiStyled } from '@mui/system';
import { theme } from 'src/theme';
import { FC, useState } from 'react';
import { RestService } from '@restgenerated/index';
import { useQuery } from '@tanstack/react-query';

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

export const BaseHomeRouter: FC = () => {
  const [open, setOpen] = useState(true);
  const { businessArea, programSlug } = useBaseUrl();
  const location = useLocation();
  const navigate = useNavigate();
  const handleDrawerOpen = (): void => {
    setOpen(true);
  };
  const handleDrawerClose = (): void => {
    setOpen(false);
  };

  const { data: businessAreaData, isLoading: businessAreaLoading } = useQuery({
    queryKey: ['businessAreasProfile', businessArea, programSlug],
    queryFn: () => {
      return RestService.restBusinessAreasUsersProfileRetrieve({
        businessAreaSlug: businessArea,
        program: programSlug === 'all' ? undefined : programSlug,
      });
    },
    staleTime: 15 * 60 * 1000, // Data is considered fresh for 15 minutes (business areas don't change often)
    gcTime: 60 * 60 * 1000, // Keep unused data in cache for 1 hour
    refetchOnWindowFocus: false, // Don't refetch when window regains focus
  });

  if (!businessAreaData || businessAreaLoading) {
    return <LoadingComponent />;
  }

  const allBusinessAreasSlugs = businessAreaData.businessAreas.map(
    (el) => el.slug,
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
