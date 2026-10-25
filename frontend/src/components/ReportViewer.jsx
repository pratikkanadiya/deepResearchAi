function safeSourceUrl(value) {
    try {
        const url = new URL(value);
        return ["http:", "https:"].includes(url.protocol) ? url.href : null;
    } catch {
        return null;
    }
}

function ReportViewer({
    report
}) {

    if (!report) {
        return null;
    }


    return (

        <section className="report">

            <h2>
                {report.metadata?.title}
            </h2>


            <div className="summary">

                <h3>
                    Executive Summary
                </h3>

                <p>
                    {report.executive_summary}
                </p>

            </div>


            <div className="sections">

                {report.sections?.map(
                    (section, index) => (

                        <article
                            key={index}
                            className="report-section"
                        >

                            <h3>
                                {section.heading}
                            </h3>

                            <p>
                                {section.content}
                            </p>


                            {section.claims?.length > 0 && (

                                <div className="claims">

                                    <h4>
                                        Evidence-backed Claims
                                    </h4>

                                    {section.claims.map(
                                        (claim, claimIndex) => (

                                            <div
                                                key={claimIndex}
                                                className="claim"
                                            >

                                                <p>
                                                    {claim.statement}
                                                </p>

                                                {claim.source_urls?.map(
                                                    (url, urlIndex) => (
                                                        safeSourceUrl(url) && (
                                                            <a
                                                                key={urlIndex}
                                                                href={safeSourceUrl(url)}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                            >
                                                                Source
                                                            </a>
                                                        )

                                                    )
                                                )}

                                            </div>

                                        )
                                    )}

                                </div>

                            )}

                        </article>

                    )
                )}

            </div>


            <div className="conclusion">

                <h3>
                    Conclusion
                </h3>

                <p>
                    {report.conclusion}
                </p>

            </div>


            <div className="limitations">

                <h3>
                    Limitations
                </h3>

                <ul>

                    {report.limitations?.map(
                        (item, index) => (

                            <li key={index}>
                                {item}
                            </li>

                        )
                    )}

                </ul>

            </div>

        </section>
    );
}


export default ReportViewer;
