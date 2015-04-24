/**
 * @file competition.cpp
 * @author Hussein Hazimeh
 * Built based on query-runner.cpp which is written by Sean Massung
 */
#include <vector>
#include <string>
#include <iostream>
#include "index/eval/ir_eval.h"
#include "util/time.h"
#include "corpus/document.h"
#include "index/inverted_index.h"
#include "index/ranker/ranker_factory.h"
#include "parser/analyzers/tree_analyzer.h"
#include "sequence/analyzers/ngram_pos_analyzer.h"
#include <cmath>
#include "index/score_data.h"
#include <random>

#include "index/forward_index.h"
#include "index/postings_data.h"

using namespace meta;


class new_ranker: public index::ranker
{
private: // Change the parameters to suit your ranking function
    double param1_ = 0.5;
    double param2_ = 0.5;

public:
    const static std::string id;
    new_ranker(); // Default Constructor
    new_ranker(double param1, double param2); // Constructor
    void set_param(double param1, double param2){param1_ = param1; param2_ = param2;}; // Sets the parameters
    double score_one(const index::score_data&); // Calculates the score for one matched term
};

const std::string new_ranker::id = "newranker"; // Used to identify the ranker in config.toml
new_ranker::new_ranker(){}
new_ranker::new_ranker(double param1, double param2) : param1_{param1}, param2_{param2} {}

double new_ranker::score_one(const index::score_data& sd)
{
    // Implement your scoring function here

    const double k1_ = 1.65;
    const double b_ = 0.82;
    const double k3_ = 500.0;
    const double mu_ = 228.0;
    // alpha = 1.0

    double doc_len = sd.idx.doc_size(sd.d_id);

    // add 1.0 to the IDF to ensure that the result is positive
    double IDF = std::log(
        1.0 + (sd.num_docs - sd.doc_count + 0.5) / (sd.doc_count + 0.5));

    double TF = ((k1_ + 1.0) * sd.doc_term_count)
                / ((k1_ * ((1.0 - b_) + b_ * doc_len / sd.avg_dl))
                   + sd.doc_term_count);

    double QTF = ((k3_ + 1.0) * sd.query_term_count)
                 / (k3_ + sd.query_term_count);

    double rank_bm25 = TF * IDF * QTF;



    double pc = static_cast<double>(sd.corpus_term_count) / sd.total_terms;

    double rank_dir = std::log(mu_/(mu_+sd.doc_size));

    if (sd.doc_term_count > 0.0)
        rank_dir += std::log(1 + sd.doc_term_count/mu_/pc);



    return param1_ * rank_bm25 + (1.0-param1_) * rank_dir;

}


namespace meta{
namespace index{
template <>
std::unique_ptr<ranker>make_ranker<new_ranker>(
        const cpptoml::table & config) // Used by new_ranker to read the parameters param1 and param2 from config.toml
{
    double param1 = 0.5; // Change to the default parameter value
    if (auto param1_file = config.get_as<double>("param1"))
        param1 = *param1_file;

    double param2 = 0.5; // Change to the default parameter value
    if (auto param2_file = config.get_as<double>("param2"))
        param2 = *param2_file;

    return make_unique<new_ranker>(param1, param2);
}

}
}





corpus::document Rocchio(corpus::document query, std::vector <std::pair<doc_id, double>> ranking, const std::shared_ptr<index::dblru_inverted_index> & idx, const std::shared_ptr<index::memory_forward_index> & fidx)
{
    const double alpha = 1.0;
    const double beta = 0.22;
    const double gamma = -0.05;
    const double n_relevant = 8.0;
    const double n_nonrelevant = 2.0;
    const double freq_threshold = 8.0;
    const double k1_ = 1.2;
    const double b_ = 0.75;


    corpus::document new_query; // Declare the new query

    /*std::cout << "-------------------------------------------" << std::endl;*/

    // Add the terms of the original query to the new query
    for (auto& qpair : query.counts()) {
    // Loop over the original query's pairs
        if (qpair.first[0]!='<') {
            new_query.increment(qpair.first, alpha*qpair.second);
            // qpair.first is the term name and qpair.second is the term frequency
            /*std::cout << qpair.first << alpha*qpair.second << std::endl;*/
        }
    }

    auto M = fidx->num_docs();
    auto avg_dl = idx->avg_doc_length();
    /*std::cout << "M = " << M << " avg_dl = " << avg_dl << std::endl;*/

    for (int i=0; i<n_relevant+n_nonrelevant; i++) {
        auto postings_list = fidx->search_primary(ranking[i].first);
        // Return the postings list of the top document in ranking

        auto term_freq = postings_list->counts();
        // term_freq contains the pairs of the form <term_id, term_freq>

        double doc_len = idx->doc_size(ranking[i].first);

        // Add the term of the top ranked document to the new query
        for (auto& tfpair : term_freq) { // Loop over the document's  pairs
            auto term_text = idx->term_text(tfpair.first); // idx->term_text converts a term id to the corresponding term name
            auto doc_freq = idx->doc_freq(tfpair.first);

            auto doc_term_freq = tfpair.second;

            // add 1.0 to the IDF to ensure that the result is positive
            double IDF = std::log(
                1.0 + (M - doc_freq + 0.5) / (doc_freq + 0.5));

            double TF = ((k1_ + 1.0) * doc_term_freq)
                        / ((k1_ * ((1.0 - b_) + b_ * doc_len / avg_dl))
                           + doc_term_freq);

            if (tfpair.second > freq_threshold
                and term_text[0] != '<'
                and term_text != "cours" and term_text != "learn"
                and i<n_relevant) {
                new_query.increment(term_text, beta/n_relevant*TF*IDF);
                /*std::cout << "+ " << term_text
                        << " doc_freq = " << doc_freq
                        << " TF-IDF = "<< TF*IDF
                        << " vector = " << beta/n_relevant*TF*IDF
                        << std::endl;*/
            }

            if (tfpair.second > freq_threshold
                and term_text[0] != '<'
                and term_text != "cours" and term_text != "learn"
                and i>=n_relevant) {
                new_query.increment(term_text, gamma/n_nonrelevant*TF*IDF);
                /*std::cout << "- " << term_text
                        << " doc_freq = " << doc_freq
                        << " TF-IDF = "<< TF*IDF
                        << " vector = " << gamma/n_nonrelevant*TF*IDF
                        << std::endl;*/
            }
        }
    }

    for (auto& qpair : new_query.counts()) {
    // Loop over the original query's pairs
        std::cout << qpair.first << " " << alpha*qpair.second << std::endl;
    }

    return new_query;
}



int main(int argc, char* argv[])
{
    index::register_ranker<new_ranker>();

    if (argc != 2 && argc != 3)
    {
        std::cerr << "Usage:\t" << argv[0] << " configFile" << std::endl;
        return 1;
    }

    // Log to standard error
    logging::set_cerr_logging();

    // Register additional analyzers
    parser::register_analyzers();
    sequence::register_analyzers();




    // Submission-specific - Ignore
    std::ofstream submission;

    submission.open("Assignment2/output.txt");
    if (!submission.is_open())
    {
        std::cout<<"Problem writing the output to the system. Make sure the program has enough writing privileges. Quiting..."<<std::endl;
        return 0;
    }
    std::string nickname;
    std::cout<<"Enter your nickname: ";
    std::getline(std::cin,nickname);
    submission<<nickname+'\n';
    // End of the submission-specific code



    //  Create an inverted index using a DBLRU cache.
    auto idx = index::make_index<index::dblru_inverted_index>(argv[1], 30000);

    auto fidx = index::make_index<index::memory_forward_index>(argv[1]); // fidx is a pointer to the forward index

    // Create a ranking class based on the config file.
    auto config = cpptoml::parse_file(argv[1]);
    auto group = config.get_table("ranker");
    if (!group)
        throw std::runtime_error{"\"ranker\" group needed in config file!"};
    auto ranker = index::make_ranker(*group);

    // Get the path to the file containing queries
    auto query_path = config.get_as<std::string>("querypath");
    if (!query_path)
        throw std::runtime_error{"config file needs a \"querypath\" parameter"};





    /*double par[10] = {0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99};
    for (int j=0; j<10; j++) {*/

    // Create an instance of ir_eval to evaluate the MAP and Precision@10 for the training queries
    auto eval = index::ir_eval(argv[1]);
    size_t i = 1;
    std::string content;

    std::ifstream queries{*query_path + *config.get_as<std::string>("dataset")
                          + "-queries.txt"};

    // Print the precision@10 and the MAP for the training queries
    while (i<=100 && queries.good())
    {
        std::getline(queries, content); // Read the content of the current training query from file

        corpus::document query{"", doc_id{i-1}}; // Instantiate the query as an empty document

        query.content(content); // Set the content of the query

        idx->tokenize(query);

        std::cout << "=======================================" << std::endl;
        std::cout << "Ranking query " << i++ << ": " << content << std::endl;
        //i++;

        // ranking is a vector of pairs of the form <docID,docScore>
        // You can access the ith document's ID using ranking[i].first and its score using ranking[i].second
        //auto ranker = make_unique<new_ranker>();
        //ranker->set_param(0.52, 0);
        auto ranking = ranker->score(*idx, query, 50);
        std::cout << "Precision@10 for this query: "
                  << eval.precision(ranking,query.id(),10) << std::endl;

        //auto new_query = Rocchio(query, ranking, idx, fidx);
        //ranking = ranker->score(*idx, new_query, 50);

        //std::cout<< "Precision@10 for this query: "<< eval.precision(ranking,query.id(),10) << std::endl;

        eval.avg_p(ranking, query.id(), 50); // Store the average precision at 50 documents for the current query

        std::cout << "Showing top 10 of " << ranking.size() << " results."<< std::endl;

        for (size_t i = 0; i < ranking.size() && i < 10; ++i)
        // Loop over the top 10 documents in ranking
            std::cout << (i + 1) << ". " << " "
                      << idx->doc_path(ranking[i].first) << " "
                      << ranking[i].second << std::endl;

        std::cout << std::endl;

    }

    std::cout << /*"par = " << par[j] << */" The MAP for the training queries is: " << eval.map() << std::endl;



    // Write the top 50 documents of each test query to the submission file
    while (queries.good())
    {
        std::getline(queries, content); // Read the content of the current testing query from file

        corpus::document query;

        query.content(content);

        //auto ranker = make_unique<new_ranker>();
        //ranker->set_param(0.52, 0);
        auto ranking = ranker->score(*idx, query, 50);
        //auto ranking = ranker->score(*idx, query, 50);
        //auto new_query = Rocchio(query, ranking, idx, fidx);
        //ranking = ranker->score(*idx, new_query, 50);

        for (size_t i=0; i < ranking.size() && i<50; i++) // Loop over the top 50 documents
        {
            submission<< std::to_string(ranking[i].first)+" "; // Write the IDs of the top 50 documents to output.txt
        }
        submission<<"\n";

    }


    submission.close();
    return 0;
}
