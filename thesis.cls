\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{thesis}[2026/08/21 Master Thesis Class]

% =======================================================
% Base class
% =======================================================
\LoadClass[
    11pt,
    a4paper,
    oneside,
    headings=big,
    bibliography=totoc,
    listof=totoc
]{scrbook}

% =======================================================
% Global fonts
% =======================================================
% Change these two packages here if you want to change the
% typography of the entire thesis.
%
% newpxtext/newpxmath = Palatino-style text + matching math.
\RequirePackage{newpxtext}
\RequirePackage{newpxmath}

% =======================================================
% Page layout
% =======================================================
\RequirePackage[
    left=30mm,
    right=25mm,
    top=25mm,
    bottom=30mm,
    headsep=8mm,
    footskip=12mm
]{geometry}

\RequirePackage{setspace}
\setstretch{1.08}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0.55em}

% =======================================================
% Typography
% =======================================================
\RequirePackage{microtype}

\setkomafont{chapter}{
    \normalfont\sffamily\bfseries\Huge
}

\setkomafont{section}{
    \normalfont\sffamily\bfseries\Large
}

\setkomafont{subsection}{
    \normalfont\sffamily\bfseries\large
}

% =======================================================
% Header / footer
% =======================================================
\RequirePackage{scrlayer-scrpage}

\clearpairofpagestyles
\ihead{\headmark}
\ohead{\pagemark}
\automark[section]{chapter}

\setkomafont{pageheadfoot}{
    \normalfont\small
}

% =======================================================
% Figures / tables
% =======================================================
\RequirePackage{graphicx}
\RequirePackage{float}
\RequirePackage{caption}
\RequirePackage{subcaption}
\RequirePackage{booktabs}
\RequirePackage{tabularx}
\RequirePackage{longtable}

\graphicspath{
    {Figures/generated/}
    {Figures/diagrams/}
    {Figures/external/}
}

\captionsetup{
    font=small,
    labelfont=bf,
    format=plain
}

% =======================================================
% Mathematics / units
% =======================================================
\RequirePackage{amsmath}
\RequirePackage{siunitx}

\numberwithin{equation}{chapter}

\sisetup{
    detect-all,
    separate-uncertainty=true,
    per-mode=symbol
}

% =======================================================
% Bibliography
% =======================================================
\RequirePackage[
    backend=biber,
    style=numeric-comp,
    sorting=none,
    maxbibnames=99
]{biblatex}

\addbibresource{Bibliography/references.bib}

% =======================================================
% Links / references
% =======================================================
\RequirePackage{xcolor}

\definecolor{ThesisBlue}{HTML}{2A5674}
\definecolor{ThesisGray}{HTML}{555555}

\RequirePackage[
    colorlinks=true,
    linkcolor=ThesisBlue,
    citecolor=ThesisBlue,
    urlcolor=ThesisBlue
]{hyperref}

\RequirePackage[
    capitalise,
    nameinlink,
    noabbrev
]{cleveref}

% =======================================================
% Project-specific commands
% =======================================================
\RequirePackage{thesis}

% =======================================================
% Title page
% =======================================================
\newcommand{\makethesistitle}{
    \begin{titlepage}
        \centering

        \vspace*{1cm}

        \includegraphics[width=0.22\textwidth]{Figures/logos/eso-logo.jpg}

        \vspace{0.4cm}
        {\LARGE \InstitutionName \par}

        \vspace{1.2cm}

        {\large \UniversityName \par}
        \vspace{0.2cm}
        {\normalsize \DepartmentName \par}

        \vfill

        \noindent\rule{\textwidth}{0.2pt}
        \vspace{0.6cm}

        {\Huge \bfseries \ThesisTitle \par}

        \vspace{0.6cm}
        {\Large \itshape \ThesisSubtitle \par}

        \vspace{0.6cm}
        \noindent\rule{\textwidth}{0.2pt}

        \vspace{0.4cm}
        {\Large Master Thesis \par}

        \vfill

        \begin{minipage}{0.55\textwidth}
            \centering
            \begin{tabular}{@{}ll@{}}
                Author:        & \AuthorName        \\
                Supervisor:    & \SupervisorName    \\
                Co-supervisor: & \CoSupervisorName  \\
                Submitted:     & \SubmissionDate
            \end{tabular}
        \end{minipage}

        \vfill
    \end{titlepage}
}
