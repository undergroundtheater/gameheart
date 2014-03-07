--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: entities_trait_addtraits; Type: TABLE; Schema: public; Owner: undergro; Tablespace: 
--

CREATE TABLE entities_trait_addtraits (
    id integer NOT NULL,
    from_trait_id integer NOT NULL,
    to_trait_id integer NOT NULL
);


ALTER TABLE public.entities_trait_addtraits OWNER TO undergro;

--
-- Name: entities_trait_addtraits_id_seq; Type: SEQUENCE; Schema: public; Owner: undergro
--

CREATE SEQUENCE entities_trait_addtraits_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.entities_trait_addtraits_id_seq OWNER TO undergro;

--
-- Name: entities_trait_addtraits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: undergro
--

ALTER SEQUENCE entities_trait_addtraits_id_seq OWNED BY entities_trait_cotraits.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: undergro
--

ALTER TABLE ONLY entities_trait_addtraits ALTER COLUMN id SET DEFAULT nextval('entities_trait_cotraits_id_seq'::regclass);


--
-- Name: entities_trait_addtraits_from_trait_id_to_trait_id_key; Type: CONSTRAINT; Schema: public; Owner: undergro; Tablespace: 
--

ALTER TABLE ONLY entities_trait_addtraits
    ADD CONSTRAINT entities_trait_addtraits_from_trait_id_to_trait_id_key UNIQUE (from_trait_id, to_trait_id);


--
-- Name: entities_trait_addtraits_pkey; Type: CONSTRAINT; Schema: public; Owner: undergro; Tablespace: 
--

ALTER TABLE ONLY entities_trait_addtraits
    ADD CONSTRAINT entities_trait_addtraits_pkey PRIMARY KEY (id);


--
-- Name: entities_trait_addtraits_from_trait_id; Type: INDEX; Schema: public; Owner: undergro; Tablespace: 
--

CREATE INDEX entities_trait_addtraits_from_trait_id ON entities_trait_cotraits USING btree (from_trait_id);

--
-- Name: entities_trait_addtraits_to_trait_id; Type: INDEX; Schema: public; Owner: undergro; Tablespace: 
--

CREATE INDEX entities_trait_addtraits_to_trait_id ON entities_trait_cotraits USING btree (to_trait_id);

--
-- Name: from_trait_id_refs_id_bebf59b8; Type: FK CONSTRAINT; Schema: public; Owner: undergro
--

ALTER TABLE ONLY entities_trait_addtraits
    ADD CONSTRAINT from_trait_id_refs_id_bebf59b8 FOREIGN KEY (from_trait_id) REFERENCES entities_trait(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: to_trait_id_refs_id_bebf59b8; Type: FK CONSTRAINT; Schema: public; Owner: undergro
--

ALTER TABLE ONLY entities_trait_addtraits
    ADD CONSTRAINT to_trait_id_refs_id_bebf59b8 FOREIGN KEY (to_trait_id) REFERENCES entities_trait(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: entities_trait_addtraits; Type: ACL; Schema: public; Owner: undergro
--

REVOKE ALL ON TABLE entities_trait_addtraits FROM PUBLIC;
REVOKE ALL ON TABLE entities_trait_addtraits FROM undergro;
GRANT ALL ON TABLE entities_trait_addtraits TO undergro;
GRANT ALL ON TABLE entities_trait_addtraits TO undergro_gameheart;


--
-- Name: entities_trait_addtraits_id_seq; Type: ACL; Schema: public; Owner: undergro
--

REVOKE ALL ON SEQUENCE entities_trait_addtraits_id_seq FROM PUBLIC;
REVOKE ALL ON SEQUENCE entities_trait_addtraits_id_seq FROM undergro;
GRANT ALL ON SEQUENCE entities_trait_addtraits_id_seq TO undergro;
GRANT SELECT ON SEQUENCE entities_trait_addtraits_id_seq TO undergro_test;


--
-- PostgreSQL database dump complete
--
