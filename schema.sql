--
-- PostgreSQL database dump
--

-- Dumped from database version 15.16 (Debian 15.16-1.pgdg13+1)
-- Dumped by pg_dump version 15.16 (Debian 15.16-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: compliance_user
--

CREATE TABLE public.audit_logs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    job_id uuid,
    tenant_id uuid NOT NULL,
    actor_type text,
    actor_id text,
    action text NOT NULL,
    previous_state jsonb,
    new_state jsonb,
    metadata jsonb,
    ip_address text,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO compliance_user;

--
-- Name: escalations; Type: TABLE; Schema: public; Owner: compliance_user
--

CREATE TABLE public.escalations (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    job_id uuid NOT NULL,
    assigned_to text,
    status text,
    resolution_notes text,
    resolved_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT escalations_status_check CHECK ((status = ANY (ARRAY['open'::text, 'in_review'::text, 'resolved'::text, 'rejected'::text])))
);


ALTER TABLE public.escalations OWNER TO compliance_user;

--
-- Name: job_events; Type: TABLE; Schema: public; Owner: compliance_user
--

CREATE TABLE public.job_events (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    job_id uuid NOT NULL,
    event_type text NOT NULL,
    event_payload jsonb,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.job_events OWNER TO compliance_user;

--
-- Name: jobs; Type: TABLE; Schema: public; Owner: compliance_user
--

CREATE TABLE public.jobs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    tenant_id uuid NOT NULL,
    external_reference text,
    event_type text NOT NULL,
    event_source text,
    payload jsonb NOT NULL,
    priority integer DEFAULT 5,
    status text NOT NULL,
    retry_count integer DEFAULT 0,
    error_message text,
    correlation_id text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    completed_at timestamp without time zone,
    CONSTRAINT jobs_status_check CHECK ((status = ANY (ARRAY['pending'::text, 'queued'::text, 'processing'::text, 'completed'::text, 'failed'::text, 'escalated'::text])))
);


ALTER TABLE public.jobs OWNER TO compliance_user;

--
-- Name: risk_results; Type: TABLE; Schema: public; Owner: compliance_user
--

CREATE TABLE public.risk_results (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    job_id uuid NOT NULL,
    tenant_id uuid NOT NULL,
    risk_score numeric(5,2),
    category text,
    confidence numeric(5,2),
    requires_escalation boolean DEFAULT false,
    explanation text,
    structured_output jsonb,
    model_provider text,
    model_name text,
    model_version text,
    prompt_version text,
    routing_strategy text,
    token_input integer,
    token_output integer,
    cost_estimate numeric(10,5),
    latency_ms integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.risk_results OWNER TO compliance_user;

--
-- Name: tenants; Type: TABLE; Schema: public; Owner: compliance_user
--

CREATE TABLE public.tenants (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL,
    status text DEFAULT 'active'::text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tenants OWNER TO compliance_user;

--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: escalations escalations_pkey; Type: CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.escalations
    ADD CONSTRAINT escalations_pkey PRIMARY KEY (id);


--
-- Name: job_events job_events_pkey; Type: CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.job_events
    ADD CONSTRAINT job_events_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_external_reference_key; Type: CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_external_reference_key UNIQUE (external_reference);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: risk_results risk_results_pkey; Type: CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.risk_results
    ADD CONSTRAINT risk_results_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: idx_audit_job; Type: INDEX; Schema: public; Owner: compliance_user
--

CREATE INDEX idx_audit_job ON public.audit_logs USING btree (job_id);


--
-- Name: idx_audit_tenant; Type: INDEX; Schema: public; Owner: compliance_user
--

CREATE INDEX idx_audit_tenant ON public.audit_logs USING btree (tenant_id);


--
-- Name: idx_escalation_job; Type: INDEX; Schema: public; Owner: compliance_user
--

CREATE INDEX idx_escalation_job ON public.escalations USING btree (job_id);


--
-- Name: idx_job_events_job; Type: INDEX; Schema: public; Owner: compliance_user
--

CREATE INDEX idx_job_events_job ON public.job_events USING btree (job_id);


--
-- Name: idx_jobs_created_at; Type: INDEX; Schema: public; Owner: compliance_user
--

CREATE INDEX idx_jobs_created_at ON public.jobs USING btree (created_at);


--
-- Name: idx_jobs_status; Type: INDEX; Schema: public; Owner: compliance_user
--

CREATE INDEX idx_jobs_status ON public.jobs USING btree (status);


--
-- Name: idx_jobs_tenant; Type: INDEX; Schema: public; Owner: compliance_user
--

CREATE INDEX idx_jobs_tenant ON public.jobs USING btree (tenant_id);


--
-- Name: idx_risk_job; Type: INDEX; Schema: public; Owner: compliance_user
--

CREATE INDEX idx_risk_job ON public.risk_results USING btree (job_id);


--
-- Name: idx_risk_tenant; Type: INDEX; Schema: public; Owner: compliance_user
--

CREATE INDEX idx_risk_tenant ON public.risk_results USING btree (tenant_id);


--
-- Name: audit_logs audit_logs_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: escalations escalations_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.escalations
    ADD CONSTRAINT escalations_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id);


--
-- Name: job_events job_events_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.job_events
    ADD CONSTRAINT job_events_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id);


--
-- Name: jobs jobs_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: risk_results risk_results_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.risk_results
    ADD CONSTRAINT risk_results_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id);


--
-- Name: risk_results risk_results_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: compliance_user
--

ALTER TABLE ONLY public.risk_results
    ADD CONSTRAINT risk_results_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- PostgreSQL database dump complete
--

\unrestrict JPIwhMnQOnDVZypZOHa6QLkxpCw9DlMGGNfK6esBNg84S9ClgmWn5JVfOTsYUj7

