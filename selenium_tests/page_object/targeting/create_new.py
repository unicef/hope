from page_object.base_components import BaseComponents


class CreateNew(BaseComponents):
  # Locators
  targetingCriteria = 'h6[data-cy="title-targeting-criteria"]'
  # Texts
  textTargetingCriteria = "Targeting Criteria"
  # Elements
  getTargetingCriteria(self):
        return self.wait_for(self.targetingCriteria)
