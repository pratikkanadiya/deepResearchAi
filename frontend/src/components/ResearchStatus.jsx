function ResearchStatus({
    result
}) {

    if (!result) {
        return null;
    }


    return (

        <div className="research-status">

            <div className="stat-card">

                <span>
                    Status
                </span>

                <strong>
                    {result.status}
                </strong>

            </div>


            <div className="stat-card">

                <span>
                    Sources
                </span>

                <strong>
                    {result.sources_count}
                </strong>

            </div>


            <div className="stat-card">

                <span>
                    Evidence
                </span>

                <strong>
                    {result.evidence_count}
                </strong>

            </div>


            <div className="stat-card">

                <span>
                    Revisions
                </span>

                <strong>
                    {result.revision_count}
                </strong>

            </div>

        </div>
    );
}


export default ResearchStatus;