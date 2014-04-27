--database changes for the 1.03.06 update

DO $$
BEGIN

    --Change in entities.models.TraitType
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.columns WHERE table_name = 'entities_traittype' AND column_name = 'labelable') 
    THEN
        ALTER TABLE entities_traittype
            ADD COLUMN labelable BOOLEAN DEFAULT FALSE;
    END IF;

    --Change in entities.models.Trait
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.columns WHERE table_name = 'entities_trait' AND column_name = 'renamable') 
    THEN
        ALTER TABLE entities_trait
            ADD COLUMN renamable BOOLEAN DEFAULT FALSE;
    END IF;

    --Change in entities.models.CharacterTrait
    IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.columns WHERE table_name = 'entities_charactertrait' AND column_name = 'label') 
    THEN
        ALTER TABLE entities_charactertrait
            ADD COLUMN label character varying(200) NULL;
    END IF;

END 
$$
